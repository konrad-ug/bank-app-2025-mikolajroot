const { test, expect } = require('@playwright/test');
const { HomePage } = require('../pages/HomePage');
const { EmployeesPage } = require('../pages/EmployeesPage');
const { EmployeeDetailsPage } = require('../pages/EmployeeDetailsPage');

test('sprawdzenie pokoju pracownika UG - Konrad Sołtys', async ({ page }) => {
  const homePage = new HomePage(page);
  const employeesPage = new EmployeesPage(page);
  const employeeDetailsPage = new EmployeeDetailsPage(page);

  await homePage.goto();
  await homePage.goToPracownicy();
  
  await employeesPage.goToSkladOsobowy();
  await employeesPage.searchEmployee('sołtys');
  
  await expect(await employeesPage.isEmployeeVisible('mgr Konrad Sołtys')).toBeTruthy();
  
  await employeesPage.clickEmployeeLink('mgr Konrad Sołtys');
  
  await expect(await employeeDetailsPage.isRoomNumberVisible('4.19')).toBeTruthy();
});
