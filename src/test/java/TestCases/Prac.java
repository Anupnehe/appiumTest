package TestCases;

import BaseTests.baseTest;
import Pages.HomePage;
import org.testng.annotations.Test;

import static org.testng.Assert.assertFalse;
import static org.testng.Assert.assertTrue;

public class Prac extends baseTest {

    @Test
    public void Login() throws InterruptedException {
        HomePage homePage = new HomePage(driver);

        assertTrue(homePage.isAccessibilityDisplayed(),"verify accessiblity displayed");
        homePage.clickOnAccessibility();

        assertTrue(homePage.isAccessibilityNodeQueryingDisplayed(),"verify accessibility node querying displayed");
        homePage.ClickonAccessibilityNodeQuerying();

        homePage.uncheckAlltheList();
        assertFalse(homePage.isAllListUncheked(),"verify all list is unchecked");
    }
}
