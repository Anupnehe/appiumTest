package Pages;

import io.appium.java_client.AppiumDriver;
import io.appium.java_client.pagefactory.AppiumFieldDecorator;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.PageFactory;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;

public class BasePage {
    protected AppiumDriver driver;

    public BasePage(AppiumDriver driver){
        this.driver= driver;
        PageFactory.initElements(new AppiumFieldDecorator(driver),this);
    }

    public void waitForElementToVisible(WebElement element){
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(30)); // Wait for up to 10 seconds
        wait.until(ExpectedConditions.visibilityOf(element));

    }

    public boolean isElementVisible(WebElement element){
        try {
            waitForElementToVisible(element);
            element.isDisplayed();
        } catch(Exception e) {

        }
        return true;
    }

    public void clickOnElement(WebElement element){
        try {
            waitForElementToVisible(element);
            element.click();
        } catch(Exception e) {

        }
    }
}


