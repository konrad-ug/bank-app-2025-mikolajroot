const { test, expect } = require('@playwright/test');

test('sprawdzenie pokoju pracownika UG - Konrad Sołtys', async ({ page }) => {

  await page.goto('https://mfi.ug.edu.pl/');
  
  await page.getByRole('banner').getByRole('link', { name: 'Pracownicy' }).click();
  
  await page.getByRole('main').getByRole('link', { name: 'skład osobowy' }).click();
  
  await page.getByRole('textbox', { name: 'Imię lub nazwisko' }).fill('sołtys');
  
  const konradLink = page.getByRole('link', { name: /mgr Konrad Sołtys/i });
  await expect(konradLink).toBeVisible();
  
  await konradLink.click();
  
  await expect(page.getByText('Nr pokoju: 4.19')).toBeVisible();
});
