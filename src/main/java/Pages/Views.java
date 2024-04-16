package Pages;

import io.appium.java_client.AppiumDriver;
import io.appium.java_client.pagefactory.AndroidFindBy;
import org.openqa.selenium.WebElement;

import java.util.NoSuchElementException;

public class Views extends BasePage{
  @AndroidFindBy(accessibility = "Date Widgets")
    private WebElement dateWidgets;

    @AndroidFindBy(accessibility = "1. Dialog")
    private WebElement dialog;

    @AndroidFindBy(accessibility = "change the date")
    private WebElement changeTheDateButton;

    @AndroidFindBy(xpath = "//*[@resource-id=\"io.appium.android.apis:id/dateDisplay\"]")
    private WebElement currentDate;

    @AndroidFindBy(accessibility = "Previous month")
    private WebElement previousMonth;

  @AndroidFindBy(accessibility = "01 January 2024")
  private WebElement newYearDate;

    @AndroidFindBy(xpath = "//android.widget.Button[@resource-id=\"android:id/button1\"]")
    private WebElement okButton;

    public Views(AppiumDriver driver) {
        super(driver);
    }

    public void clickOnDateWidget(){
        clickOnElement(dateWidgets);
    }

  public void clickOnDialog(){
    clickOnElement(dialog);
  }
  public boolean IsDialogDisplayed(){
    return isElementVisible(dialog);
  }

  public boolean isCurrentDateDisplayed(){
    return isElementVisible(currentDate);
  }

  public boolean isDateWidgetDisplayed(){
      return isElementVisible(dateWidgets);
  }

  public void enterNewYearDateTextBox() {
    clickOnElement(changeTheDateButton);
    int MAX_ATTEMPTS = 12;
    if (!isElementVisible(newYearDate,10)) {
      for (int i = 0; i < MAX_ATTEMPTS; i++) {
        try {
          clickOnElement(previousMonth);
          if(isElementVisible(newYearDate,15)) {
            break;
          }
        } catch (NoSuchElementException e) {
          break;
        }
      }
    }
    if (isElementVisible(newYearDate)) {
      clickOnElement(newYearDate);
      clickOnElement(okButton);
    }
  }
}
