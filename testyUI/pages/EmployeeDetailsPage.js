class EmployeeDetailsPage {
  constructor(page) {
    this.page = page;
  }

  async getRoomNumber() {
    return this.page.getByText(/Nr pokoju:/);
  }

  async isRoomNumberVisible(roomNumber) {
    const roomElement = this.page.getByText(`Nr pokoju: ${roomNumber}`);
    return await roomElement.isVisible();
  }
}

module.exports = { EmployeeDetailsPage };
