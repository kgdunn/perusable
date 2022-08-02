
describe('Perusable', function ()
{
  it('Displays the home page.', function ()
  {
    cy.visit('/');
    cy.get('h1').should('contain', 'Perusable');
  });
});


it('Displays a list of results.', function ()
{
  cy.visit('/');
  cy.get('input#query').type('cabernet');
  cy.get('button').contains('Search').click();
  cy.get('div.card-title').should('contain', 'Cabernet Sauvignon');
});
