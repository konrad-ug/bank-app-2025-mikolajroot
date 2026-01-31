class HomePage {
  constructor(page) {
    this.page = page;
    this.pracownicyLink = page.getByRole('banner').getByRole('link', { name: 'Pracownicy' });
  }

  async goto() {
    await this.page.goto('https://mfi.ug.edu.pl/');
  }

  async goToPracownicy() {
    await this.pracownicyLink.click();
  }
}

module.exports = { HomePage };
