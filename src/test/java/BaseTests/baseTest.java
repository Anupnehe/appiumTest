package BaseTests;

import drivers.DriverManager;
import io.appium.java_client.AppiumDriver;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;

public class baseTest  extends DriverManager {
    public AppiumDriver driver;

@BeforeMethod
    public void setUp(){
        this.driver = DriverManager.getDriver();
    }


    @AfterMethod
    public void tearDown(){
    driver.quit();
    }
}
