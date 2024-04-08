package Pages;

import io.appium.java_client.AppiumDriver;
import io.appium.java_client.pagefactory.AndroidFindBy;
import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;

public class HomePage extends BasePage {
    @AndroidFindBy(accessibility = "Access'ibility")
    private WebElement aaccessibility;

    @AndroidFindBy(accessibility = "Accessibility Node Querying")
    private WebElement accessibilityNodeQuerying;

    @AndroidFindBy(accessibility = "Preference")
    private WebElement preference;

    @AndroidFindBy(accessibility = "Views")
    private WebElement views;

    public HomePage(AppiumDriver driver) {
        super(driver);
    }

    public void clickOnAccessibility(){
        clickOnElement(aaccessibility);
    }

    public boolean isAccessibilityDisplayed(){
        return isElementVisible(aaccessibility);
    }
    public void ClickonAccessibilityNodeQuerying(){
        clickOnElement(accessibilityNodeQuerying);
    }

    public boolean isAccessibilityNodeQueryingDisplayed(){
        return isElementVisible(accessibilityNodeQuerying);
    }

    public void uncheckTheCheckedList(){

        for(int i=1;i<=7;i++){
            WebElement ele = driver.findElement(By.xpath("//*[@resource-id=\"android:id/list\"]/descendant::android.widget.CheckBox["+i+"]"));
            ele.click();
        }
    }

    public void uncheckAlltheList(){

        for(int i=1;i<=7;i++){
            WebElement ele = driver.findElement(By.xpath("//*[@resource-id=\"android:id/list\"]/descendant::android.widget.CheckBox["+i+"]"));
            String checkedStatus=ele.getAttribute("checked");
            if(checkedStatus.equalsIgnoreCase("true")){
            ele.click();
            }
        }
    }

    public boolean isAllListUncheked(){

        for(int i=1;i<=7;i++){
            WebElement ele = driver.findElement(By.xpath("//*[@resource-id=\"android:id/list\"]/descendant::android.widget.CheckBox["+i+"]"));
            String checkedStatus=ele.getAttribute("checked");
            if(checkedStatus.equalsIgnoreCase("true")){
                return true;
            }
        }
        return false;
    }

    public PreferencePage clickOnPreference(){
        clickOnElement(preference);
        return new PreferencePage(driver);
    }

    public boolean isPreferencDisplayed(){
        return isElementVisible(preference);
    }

    public Views clickOnViews(){
        clickOnElement(views);
        return new Views(driver);
    }

}

