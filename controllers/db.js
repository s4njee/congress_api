const knex = require('knex')({
    client: 'pg',
    connection: {
        connectionString: `postgresql://postgres:postgres@localhost:5432/csearch`,
        ssl: false
    }
});


module.exports = {knex}