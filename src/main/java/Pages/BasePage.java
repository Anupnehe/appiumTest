package Pages;

import io.appium.java_client.AppiumDriver;
import io.appium.java_client.pagefactory.AppiumFieldDecorator;
import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.PageFactory;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;

import static java.time.Duration.ofSeconds;

public class BasePage {
    protected AppiumDriver driver;

    public BasePage(AppiumDriver driver){
        this.driver= driver;
        PageFactory.initElements(new AppiumFieldDecorator(driver),this);
    }

    public void waitForElementToVisible(WebElement element){
        WebDriverWait wait = new WebDriverWait(driver, ofSeconds(30)); // Wait for up to 10 seconds
        wait.until(ExpectedConditions.visibilityOf(element));

    }
    protected boolean isElementVisible(WebElement element, int waitTime) {
        try {
            waitForElementToBeVisible(element ,waitTime);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    private void waitForElementToBeVisible(WebElement element) {
        WebDriverWait wait = new WebDriverWait(driver, ofSeconds(30));
        wait.until(ExpectedConditions.visibilityOf(element));
    }

    private void waitForElementToBeVisible(WebElement element,int waitTime) {
        WebDriverWait wait = new WebDriverWait(driver, ofSeconds(waitTime));
        wait.until(ExpectedConditions.visibilityOf(element));
    }

    protected boolean isElementVisible(WebElement element) {
        try {
            waitForElementToBeVisible(element);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    public void clickOnElement(WebElement element){
        try {
            waitForElementToVisible(element);
            element.click();
        } catch(Exception e) {

        }
    }

    public void sendTextTobox(WebElement element,String string ){
        try {
            waitForElementToVisible(element);
            element.sendKeys(string);
        } catch(Exception e) {

        }
    }
}


