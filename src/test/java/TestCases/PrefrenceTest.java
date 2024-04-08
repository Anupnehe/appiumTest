package TestCases;

import BaseTests.baseTest;
import Pages.HomePage;
import Pages.PreferencePage;
import org.testng.annotations.Test;

import static org.testng.Assert.assertTrue;
import static org.testng.AssertJUnit.assertEquals;


public class PrefrenceTest extends baseTest {

@Test
    public void PrefrencesFromXml(){
    HomePage homePage = new HomePage(driver);
    assertTrue(homePage.isPreferencDisplayed(),"verify Preferenc Displayed ");

    PreferencePage PreferencePage=homePage.clickOnPreference();
    assertTrue(PreferencePage.isPreferencesFromXMLDisplayed(),"verify preferences from XML Displayed ");

    PreferencePage.ClickOnPreferencesFromXML();
    assertTrue(PreferencePage.isPreferencesFromXMLHederDisplayed(),"verify preferences from XML header Displayed ");

    PreferencePage.ClickOnCheckboxPreferences();
    PreferencePage.clickOnEditTextPrefernce("dog");

    PreferencePage.ClickOnListPreferences();
    assertTrue(PreferencePage.isLaunchPreferenceDisplayed(),"verify Launch Preference text Displayed ");
    assertTrue(PreferencePage.isPreferenceAttributeDisplayed(),"verify Preference attribute text Displayed ");

    PreferencePage.ClickOnParentCheckboxPreferences();
    PreferencePage.ClickOnChildCheckboxPreferences();

    PreferencePage.ClickOnInternetPreferences();
    assertTrue(PreferencePage.isUrlDisplayed());

    }
}
