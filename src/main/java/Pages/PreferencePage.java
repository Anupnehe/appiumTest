package Pages;

import io.appium.java_client.AppiumDriver;
import io.appium.java_client.pagefactory.AndroidFindBy;
import org.openqa.selenium.WebElement;

public class PreferencePage extends BasePage{

    @AndroidFindBy(accessibility = "1. Preferences from XML")
    private WebElement preferencesFromXML;

    @AndroidFindBy(xpath = "//*[@text=\"Preference/1. Preferences from XML\"]")
    private WebElement preferencesFromXMLHeder;

    @AndroidFindBy(xpath = "(//*[@resource-id=\"android:id/widget_frame\"])[1]")
    private WebElement checckBoxPreference;

    @AndroidFindBy(xpath = "//*[@resource-id=\"android:id/list\"]/android.widget.LinearLayout[2]")
    private WebElement EditTextPrfrence;

    @AndroidFindBy(xpath = "//*[@resource-id=\"android:id/edit\"]")
    private WebElement EditTextPrfrenceBox;

    @AndroidFindBy(xpath = "//*[@resource-id=\"android:id/button1\"]")
    private WebElement okButton;

    @AndroidFindBy(xpath = "//*[@resource-id=\"android:id/title\" and @text=\"List preference\"]")
    private WebElement listPrfrence;

    @AndroidFindBy(xpath = "//*[@resource-id=\"android:id/text1\" and @text=\"Alpha Option 01\"]")
    private WebElement alphaOption;
    @AndroidFindBy(xpath = "(//*[@resource-id=\"android:id/checkbox\"])[2]")
    private WebElement parentCheckBox;

    @AndroidFindBy(xpath = "(//*[@resource-id=\"android:id/checkbox\"])[3]")
    private WebElement childCheckBox;

    @AndroidFindBy(xpath = "//*[@resource-id=\"android:id/title\" and @text=\"Launch preferences\"]")
    private WebElement launchPreferenceText;

    @AndroidFindBy(xpath = "//*[@resource-id=\"android:id/title\" and @text=\"Preference attributes\"]")
    private WebElement PreferenceAttributeText;

    @AndroidFindBy(xpath = "//*[@resource-id=\"android:id/title\" and @text=\"Intent preference\"]")
    private WebElement internetPreference;



    public PreferencePage(AppiumDriver driver) {
        super(driver);
    }

    public void ClickOnPreferencesFromXML(){
        clickOnElement(preferencesFromXML);
    }
    public boolean isPreferencesFromXMLDisplayed(){
        return isElementVisible(preferencesFromXML);
    }
    public boolean isPreferencesFromXMLHederDisplayed(){
        return isElementVisible(preferencesFromXMLHeder);
    }

    public void clickOnEditTextPrefernce (String text){
        clickOnElement(EditTextPrfrence);
        EditTextPrfrenceBox.sendKeys(text);
        clickOnElement(okButton);
    }

    public void ClickOnCheckboxPreferences(){
        clickOnElement(checckBoxPreference);
    }
    public void ClickOnListPreferences(){
        clickOnElement(listPrfrence);
        clickOnElement(alphaOption);
    }

    public void ClickOnParentCheckboxPreferences(){
        clickOnElement(parentCheckBox);
    }

    public void ClickOnChildCheckboxPreferences(){
        String enable=childCheckBox.getAttribute("enabled");
        if(enable.equalsIgnoreCase("true")) {
            clickOnElement(childCheckBox);
        }
    }

    public boolean isLaunchPreferenceDisplayed(){
        return isElementVisible(launchPreferenceText);
    }

    public boolean isPreferenceAttributeDisplayed(){
        return isElementVisible(PreferenceAttributeText);
    }

    public void ClickOnInternetPreferences(){
        clickOnElement(internetPreference);
    }
    public boolean isUrlDisplayed(){
        String url=driver.getPageSource();
        try {
            Thread.sleep(3000);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
        return url.contains("android.com");
    }
}
