def test_config():
    from config.AppConfig import AppConfig
    config = AppConfig("config/")
    assert config.systemConfig is not None
    assert config.clientConfig is not None
    assert config.motorConfig is not None
    assert config.motorConfig.firingMotor is not None
    assert config.motorConfig.chamberServo is not None
    assert config.cameraConfig is not None

    configClasses = [config.systemConfig, config.clientConfig, config.motorConfig, 
                     config.motorConfig.aimMotors.panMotor, config.motorConfig.aimMotors.tiltMotor, 
                     config.motorConfig.firingMotor, config.motorConfig.chamberServo, config.cameraConfig]

    for configClass in configClasses:
        missing_fields = []

        print()
        print(configClass)
        for name, value in vars(configClass).items():
            print(name, value)
            if value is None or value == "":
                missing_fields.append(name)

        assert not missing_fields, f"Missing values: {missing_fields}"
        