package Pages;

import io.appium.java_client.AppiumDriver;
import io.appium.java_client.pagefactory.AndroidFindBy;
import org.openqa.selenium.WebElement;

import java.util.NoSuchElementException;

public class Controls extends BasePage{
  @AndroidFindBy(accessibility = "Controls")
  private WebElement controls;

  @AndroidFindBy(accessibility = "1. Light Theme")
  private WebElement lightTheme;

  @AndroidFindBy(id = "io.appium.android.apis:id/edit")
  private WebElement hintTextBox;

  @AndroidFindBy(accessibility = "Checkbox 1")
  private WebElement checkBox1;

  @AndroidFindBy(accessibility = "RadioButton 1")
  private WebElement radioButton1;

  @AndroidFindBy(accessibility = "Star")
  private WebElement starButton;

  @AndroidFindBy(accessibility = "io.appium.android.apis:id/toggle1")
  private WebElement offButton;



    public Controls(AppiumDriver driver) {
        super(driver);
    }

    public void clickOnControls(){
      clickOnElement(controls);
    }

  public boolean isLightThemeDisplayed(){
    isElementVisible(lightTheme);
      return true;
  }
 public void sendTextToHintBox(){
   sendTextTobox(hintTextBox,"Hello");
 }

 public  void clickOnCheckBox(){
      clickOnElement(checkBox1);
 }
  public  void clickOnRadioBox(){
    clickOnElement(radioButton1);
  }

  public  void clickOnStarButton(){
    clickOnElement(starButton);
  }

  public  void clickOnOffButton(){
    clickOnElement(offButton);
  }
}
