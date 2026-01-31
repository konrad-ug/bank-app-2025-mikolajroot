class EmployeesPage {
  constructor(page) {
    this.page = page;
    this.skladOsobowyLink = page.getByRole('main').getByRole('link', { name: 'skład osobowy' });
    this.searchInput = page.getByRole('textbox', { name: 'Imię lub nazwisko' });
  }

  async goToSkladOsobowy() {
    await this.skladOsobowyLink.click();
  }

  async searchEmployee(name) {
    await this.searchInput.fill(name);
  }

  async clickEmployeeLink(employeeName) {
    const employeeLink = this.page.getByRole('link', { name: new RegExp(employeeName, 'i') });
    await employeeLink.click();
  }

  async isEmployeeVisible(employeeName) {
    const employeeLink = this.page.getByRole('link', { name: new RegExp(employeeName, 'i') });
    return await employeeLink.isVisible();
  }
}

module.exports = { EmployeesPage };
