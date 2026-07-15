package drivers;

import io.appium.java_client.AppiumDriver;
import org.openqa.selenium.remote.DesiredCapabilities;

import java.net.MalformedURLException;
import java.net.URL;

public class DriverManager {

    private static  ThreadLocal<AppiumDriver>appiumDriver= new ThreadLocal<>();
public static AppiumDriver getDriver(){
    DesiredCapabilities capabilities = new DesiredCapabilities();
    capabilities.setCapability("platformName","android");
    capabilities.setCapability("appium:app","A:\\app\\android-apidemos\\apks\\ApiDemos-debug.apk");
    capabilities.setCapability("appium:automationName","UIAutomator2");
    capabilities.setCapability("appium:deviceName","SWT8IFV8F6WWQO8T");

    try {
        appiumDriver.set(new AppiumDriver(new URL("http://127.0.0.1:4723"),capabilities));
    } catch (MalformedURLException e) {
        throw new RuntimeException(e);
    }


    return appiumDriver.get();
}
}
