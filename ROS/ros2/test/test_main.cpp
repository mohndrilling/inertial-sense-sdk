#include "gtest_helpers.h"
#include "test_main.h"

//auto testNode = std::make_shared<cTestNode>();
TEST(test_main, basic)
{
    auto testNode = std::make_shared<cTestNode>();
    testNode->init();
    //rclcpp::spin_some(testNode);
    std::string yaml = "topic: \"inertialsense\"\n"
                       "port: [/dev/ttyACM0, /dev/ttyACM1, /dev/ttyACM2]\n"
                       "baudrate: 921600\n"
                       "\n"
                       "ins:\n"
                       "  navigation_dt_ms: 16                          # EKF update period.  uINS-3: 4  default, 1 max.  Use `msg/ins.../period` to reduce INS output data rate."
                       "\n"
                       "sensors:\n"
                       "  messages:  \n"
                       "    pimu:             # Publish preintegrated IMU delta theta and delta velocity\n"
                       "      topic: \"pimu\"\n"
                       "      enable: true\n"
                       "      period: 1\n";

    YAML::Node config = YAML::Load(yaml);
    ASSERT_TRUE(config.IsDefined()) << "Unable to parse YAML file. Is the file valid?";

    InertialSenseROS isROS(config);
    isROS.initialize();

    bool success = false;
    unsigned int startTimeMs = current_timeMs(), prevTimeMs = 0, nowTimeMs;
	while((nowTimeMs = current_timeMs()) - startTimeMs < 5000)
	{
            isROS.update();
	    rclcpp::spin_some(testNode);
        if (testNode->did_rx_pimu_) {
            success = true;
            break;
        } else {
            // check regularly, but don't print regularly..
            SLEEP_MS(200);
            if (prevTimeMs / 1000 != nowTimeMs / 1000) {
                TEST_COUT << "waiting...  (time: " << nowTimeMs << ")" << std::endl;
                prevTimeMs = nowTimeMs;
            }
        }
    }

    ASSERT_TRUE( success );
    isROS.terminate();
}

/**
 * In this test, are are confirming that the GPS, INS, and IMU messages output "comparable" time stamps.  IMU outputs seconds since startup (double) ONLY (it does not change with GPS fix, etc).
 * GPS outputs tow as millis, and it is set when GPS fix is achieved.  The time updates at the rate (and with the value) from the GPS signal.
 * INS outputs tow as fractional seconds since startup, UNTIL a GPS fix is made. Once a GPS fix is made, we get a "week" value (number of weeks since 1980), and then our timeOfWeek is updated to
 * the GPS timeOfWeek (in fractional seconds) - it is effectively a fusion of the IMU time and the GPS time.
 *
 * In inertial-sense-ros, we do some maths to try publish them both in RosTime::Time messages, as seconds/nanos.
 *
 * In this test, we subscribe to INS_1, GPS_1 and IMU, and also DID_GPS1_TIMEPULSE.  Once we get a GPS fix, we a set of messages over 10 seconds.  Then, we take the average difference between the INS timestamp
 * and the nearest GPS timestamp.  The average deviation should be below <0.5s, but ideally is below 0.1s.
 * DID_GPS1_TIMEPULSE provides the towOffset, timeMcu (effectively time since bootup)
 */
TEST(test_main, gps_ins_time_sync)
{
    auto testNode = std::make_shared<cTestNode>();
    testNode->init();
    std::string yaml = "topic: \"inertialsense\"\n"
                       "port: [/dev/ttyACM0, /dev/ttyACM1, /dev/ttyACM2]\n"
                       "baudrate: 921600\n"
                       "\n"
                       "ins:\n"
                       "  navigation_dt_ms: 16\n"
                       "  messages:\n"
                       "    odom_ins_enu:\n"
                       "      topic: \"odom_ins_enu\"\n"
                       "      enable: true\n"
                       "\n"
                       "sensors:\n"
                       "  messages:  \n"
                       "    imu:\n"
                       "      topic: \"imu\"\n"
                       "      enable: true\n"
                       "      period: 1\n"
                       "    pimu:\n"
                       "      topic: \"pimu\"\n"
                       "      enable: true\n"
                       "      period: 1\n"
                       "\n"
                       "gps1:\n"
                       "  type: 'F9P'\n"
                       "  gpsTimeUserDelay: 0.0\n"
                       "  messages:\n"
                       "    pos_vel:\n"
                       "      topic: \"gps1/pos_vel\"\n"
                       "      enable: true\n"
                       "      period: 1";

    YAML::Node config = YAML::Load(yaml);
    ASSERT_TRUE(config.IsDefined()) << "Unable to parse YAML file. Is the file valid?";

    InertialSenseROS isROS(config);
    isROS.initialize();

    testNode->quiet = true;

    bool success = false;
    unsigned int startTimeMs = current_timeMs(), prevTimeMs = 0, nowTimeMs;
    while( ((nowTimeMs = current_timeMs()) - startTimeMs < 10000) && !testNode->got_gps_tow )
    {
        isROS.update();
        rclcpp::spin_some(testNode);
        // check regularly, but don't print regularly..
        SLEEP_MS(100);
        if (prevTimeMs / 2500 != nowTimeMs / 2500) {
            TEST_COUT << "Waiting for GPS Fix/TimeOfWeek Update...  (time: " << (nowTimeMs - startTimeMs) / 1000.0 << ")" << std::endl;
            prevTimeMs = nowTimeMs;
        }
    }

    ASSERT_TRUE(testNode->got_gps_tow) << "Timeout waiting for TimeOfWeek to set (Poor GPS Signal?). Unable to perform relevant tests." << std::endl;
    TEST_COUT << "Got TimeOfWeek/GPS Fix.  Collecting 10 seconds of data..." << std::endl;

    startTimeMs = current_timeMs(), prevTimeMs = 0;
    while((nowTimeMs = current_timeMs()) - startTimeMs < 10000)
    {
        isROS.update();
        rclcpp::spin_some(testNode);
        // check regularly, but don't print regularly..
        SLEEP_MS(100);
        if (prevTimeMs / 2500 != nowTimeMs / 2500) {
            TEST_COUT << "Collecting data...  (" << 10.0 - (nowTimeMs - startTimeMs) / 1000.0 << "sec remaining)" << std::endl;
            prevTimeMs = nowTimeMs;
        }
    }

    TEST_COUT << "Timestamp Deviation (GPS <> pIMU):  [" << testNode->get_min_deviation(testNode->gps_ts, testNode->pimu_ts) << " <= " <<  testNode->get_avg_deviation(testNode->gps_ts, testNode->pimu_ts) << " <= "  << testNode->get_max_deviation(testNode->gps_ts, testNode->pimu_ts) << "]" << :: std::endl;
    TEST_COUT << "Timestamp Deviation (GPS <> IMU):   [" << testNode->get_min_deviation(testNode->gps_ts, testNode->imu_ts)  << " <= " <<  testNode->get_avg_deviation(testNode->gps_ts, testNode->imu_ts) << " <= "  << testNode->get_max_deviation(testNode->gps_ts, testNode->imu_ts) << "]" << :: std::endl;
    TEST_COUT << "Timestamp Deviation (GPS <> INS):   [" << testNode->get_min_deviation(testNode->gps_ts, testNode->ins_ts)  << " <= " <<  testNode->get_avg_deviation(testNode->gps_ts, testNode->ins_ts) << " <= "  << testNode->get_max_deviation(testNode->gps_ts, testNode->ins_ts) << "]" << :: std::endl;
    TEST_COUT << "Timestamp Deviation (INS <> IMU):   [" << testNode->get_min_deviation(testNode->ins_ts, testNode->imu_ts)  << " <= " <<  testNode->get_avg_deviation(testNode->ins_ts, testNode->imu_ts) << " <= "  << testNode->get_max_deviation(testNode->ins_ts, testNode->imu_ts) << "]" << :: std::endl;

    EXPECT_GE( 0.05,  testNode->get_avg_deviation(testNode->gps_ts, testNode->pimu_ts));
    EXPECT_GE( 0.05,  testNode->get_avg_deviation(testNode->gps_ts, testNode->imu_ts));
    EXPECT_GE( 0.05,  testNode->get_avg_deviation(testNode->gps_ts, testNode->ins_ts));
    EXPECT_GE( 0.005, testNode->get_avg_deviation(testNode->ins_ts, testNode->imu_ts));
    isROS.terminate();
}


void cTestNode::init()
{
    //auto testNode = std::make_shared<cTestNode>();
    //testNode->init();

    //auto nh = std::make_shared<rclcpp::Node>("nh");
    sub_wheel_encoder_      = this->create_subscription<sensor_msgs::msg::JointState>("msg_wheel_encoder", 1, std::bind(&cTestNode::cbWheelEncoder, this, std::placeholders::_1));
    sub_pimu_               = this->create_subscription<inertial_sense_ros2::msg::PIMU>("pimu", 1, std::bind(&cTestNode::cbPIMU, this, std::placeholders::_1));
    sub_imu_                = this->create_subscription<sensor_msgs::msg::Imu>("imu", 1, std::bind(&cTestNode::cbIMU, this, std::placeholders::_1));
    sub_ins_                = this->create_subscription<nav_msgs::msg::Odometry>("odom_ins_enu", 1, std::bind(&cTestNode::cbINS, this, std::placeholders::_1));
    sub_gps1_               = this->create_subscription<inertial_sense_ros2::msg::GPS>("gps1/pos_vel", 1, std::bind(&cTestNode::cbGPS, this, std::placeholders::_1));
}

bool cTestNode::step()
{
    // static double last_time = 0;
    // if( ros::ok() )
    // {
    //     double current_time = ros::Time::now().toSec();
    //     double dt = current_time - last_time;
    //     last_time = current_time;
    //     ros::spinOnce();
    //     current_time = ros::Time::now().toSec();
    //     ros::Rate rate(50);     // 50 ms
    //     rate.sleep();
    //     dt = ros::Time::now().toSec() - current_time;

    //     return true;
    // }

    return false;
}

void cTestNode::cbWheelEncoder(const sensor_msgs::msg::JointState &msg)
{
    if (!quiet)
        TEST_COUT << "Rx wheel encoder : " << std::fixed << std::setw(11) << std::setprecision(6) << msg.header.stamp.sec << std::endl;
}

void cTestNode::cbPIMU(const inertial_sense_ros2::msg::PIMU::SharedPtr pimu)
{
    if (!quiet)
        TEST_COUT << "Rx PIMU : " << std::fixed << std::setw(11) << std::setprecision(6) << pimu->header.stamp.sec << std::endl;
    if (got_gps_tow)
        pimu_ts.push_back(pimu->header.stamp.sec);
    this->did_rx_pimu_ = true;
}

void cTestNode::cbIMU(const  sensor_msgs::msg::Imu &imu)
{
    if (!quiet)
        TEST_COUT << "Rx IMU : " << std::fixed << std::setw(11) << std::setprecision(6) << imu.header.stamp.sec << std::endl;
    if (got_gps_tow)
        imu_ts.push_back(imu.header.stamp.sec);
}

void cTestNode::cbINS(const nav_msgs::msg::Odometry &ins)
{
    if (!quiet)
        TEST_COUT << "Rx INS : " << std::fixed << std::setw(11) << std::setprecision(6) << ins.header.stamp.sec << std::endl;
    if (got_gps_tow)
        ins_ts.push_back(ins.header.stamp.sec);
}

void cTestNode::cbGPS(const inertial_sense_ros2::msg::GPS &gps)
{
    if (!quiet)
        TEST_COUT << "Rx GPS : " << std::fixed << std::setw(11) << std::setprecision(6) << gps.header.stamp.sec << std::endl;
    gps_ts.push_back(gps.header.stamp.sec);
    got_gps_tow = true;
}


int cTestNode::get_deviations(std::vector<double> &a, std::vector<double> &b, std::vector<double> &out) {
    double total_devs = 0.0;

    out.clear();
    for (auto aa : a) {
        double min_d = 99999999.;
        // find the value from b with the nearest difference to aa
        for (auto bb : b) {
            min_d = std::min(min_d, std::abs(aa - bb));
        }
        out.push_back(min_d);
        total_devs += min_d;
    }
    return out.size();
}

double cTestNode::get_avg_deviation(std::vector<double> &a, std::vector<double> &b) {

    std::vector<double> devs;
    int num = get_deviations(a, b, devs);
    double total_devs = 0.0;

    for (auto d : devs) {
        total_devs += d;
    }
    return total_devs / (double)devs.size();
}

double cTestNode::get_min_deviation(std::vector<double> &a, std::vector<double> &b) {
    double min_d = 999999999.;

    std::vector<double> devs;
    int num = get_deviations(a, b, devs);

    for (auto d : devs) {
        min_d = std::min(min_d, d);
    }
    return min_d;
}

double cTestNode::get_max_deviation(std::vector<double> &a, std::vector<double> &b) {
    double max_d = 0.;

    std::vector<double> devs;
    int num = get_deviations(a, b, devs);

    for (auto d : devs) {
        max_d = std::max(max_d, d);
    }
    return max_d;
}
int main(int argc, char** argv)
{
    rclcpp::init(argc, argv);
    ::testing::InitGoogleTest(&argc, argv);
    //auto testNode = std::make_shared<cTestNode>();
    //testNode->init();
   // auto node = std::make_shared<rclcpp::Node>("test_inertial_sense_ros");
    // Create a MultiThreadedExecutor with 1 thread
    //rclcpp::executors::MultiThreadedExecutor executor(rclcpp::ExecutorOptions(), 1);
    // Add the node to the executor
    //executor.add_node(node);
    // Spin the executor (similar to async spinner)
    //rclcpp::spin_some(testNode);
    int ret = RUN_ALL_TESTS();
    //spinner.stop();
    rclcpp::shutdown();
    return ret;
}