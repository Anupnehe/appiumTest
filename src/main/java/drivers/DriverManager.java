package drivers;

import io.appium.java_client.AppiumDriver;
import io.appium.java_client.service.local.AppiumDriverLocalService;
import io.appium.java_client.service.local.AppiumServiceBuilder;
import io.appium.java_client.service.local.flags.GeneralServerFlag;
import org.openqa.selenium.remote.DesiredCapabilities;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.URL;

public class DriverManager {

    private static final ThreadLocal<AppiumDriver> appiumDriver = new ThreadLocal<>();
    private static AppiumDriverLocalService server;

    /**
     * Programmatically starts the Appium Server on a dynamically allocated free port.
     */
    public static void startServer() {
        if (server == null || !server.isRunning()) {
            AppiumServiceBuilder builder = new AppiumServiceBuilder()
                    .withIPAddress("127.0.0.1")
                    .usingAnyFreePort() // Dynamically finds and assigns an available port
                    .withArgument(GeneralServerFlag.SESSION_OVERRIDE) // Overwrites active sessions if any crash
                    .withArgument(GeneralServerFlag.LOG_LEVEL, "info");

            server = AppiumDriverLocalService.buildService(builder);
            server.start();
            System.out.println("Appium Server started successfully at: " + server.getUrl());
        }
    }

    /**
     * Programmatically stops the running Appium Server.
     */
    public static void stopServer() {
        if (server != null && server.isRunning()) {
            server.stop();
            System.out.println("Appium Server stopped.");
        }
    }

    /**
     * Executes 'adb devices' and returns the UDID of the first connected active device.
     */
    private static String getConnectedDeviceUdid() {
        try {
            Process process = new ProcessBuilder("adb", "devices").start();
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;

            while ((line = reader.readLine()) != null) {
                line = line.trim();
                // adb output format is: "[udid]   device"
                if (!line.isEmpty() && !line.startsWith("List of devices") && line.contains("device")) {
                    String udid = line.split("\\s+")[0];
                    System.out.println("Auto-detected Android UDID: " + udid);
                    return udid;
                }
            }
        } catch (Exception e) {
            System.err.println("Failed to detect devices via adb. Ensure ADB is in your system PATH.");
        }
        throw new RuntimeException("No active Android device found! Make sure your device/emulator is connected via ADB.");
    }

    public static AppiumDriver getDriver() {
        if (appiumDriver.get() == null) {
            // 1. Ensure the server is running
            startServer();

            // 2. Fetch the connected UDID dynamically
            String udid = getConnectedDeviceUdid();

            DesiredCapabilities capabilities = new DesiredCapabilities();
            capabilities.setCapability("platformName", "android");
            capabilities.setCapability("appium:app", "A:\\app\\android-apidemos\\apks\\ApiDemos-debug.apk");
            capabilities.setCapability("appium:automationName", "UIAutomator2");
            capabilities.setCapability("appium:deviceName", udid); // Automatically updates deviceName to the UDID
            capabilities.setCapability("appium:udid", udid);       // Explicitly target the correct device

            // 3. Connect driver to the dynamically started server URL
            URL serverUrl = server.getUrl();
            appiumDriver.set(new AppiumDriver(serverUrl, capabilities));
        }

        return appiumDriver.get();
    }

    /**
     * Destroys the driver instance for the current thread.
     */
    public static void quitDriver() {
        if (appiumDriver.get() != null) {
            appiumDriver.get().quit();
            appiumDriver.remove();
        }
    }
}