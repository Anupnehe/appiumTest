package TestCases;

import BaseTests.baseTest;
import Pages.HomePage;
import Pages.Views;
import org.testng.annotations.Test;
import static org.testng.Assert.assertTrue;

public class ViewsTest extends baseTest {
    @Test
    public void DateAndTimeWidgets(){
        HomePage homePage = new HomePage(driver);
        Views views=homePage.clickOnViews();

        assertTrue(views.isDateWidgetDisplayed(),"verify date widget displayed");
        views.clickOnDateWidget();

        assertTrue(views.IsDialogDisplayed(),"verify dialog displayed");
        views.clickOnDialog();

        assertTrue(views.isCurrentDateDisplayed(),"verify current date displayed");
        views.enterNewYearDateTextBox();
    }
}
