class EmployeeDetailsPage {
  constructor(page) {
    this.page = page;
  }

  async getRoomNumber() {
    return this.page.getByText(/Nr pokoju:/);
  }

  async isRoomNumberVisible(roomNumber) {
    const roomElement = this.page.getByText(new RegExp(`\\*?Nr pokoju:\\s*${roomNumber}`));
    return await roomElement.isVisible();
  }

  async isWorkingAtInstitute(instituteName) {
    const instituteElement = this.page.getByText(instituteName);
    return await instituteElement.isVisible();
  }
}

module.exports = { EmployeeDetailsPage };
