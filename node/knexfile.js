// Update with your config settings.

module.exports = {

    development: {
        client: 'pg',
        connection: {
            host: 'db',
            database: 'congress',
            user: 'username',
        },
        pool: {
            min: 2,
            max: 10
        },
    },

    staging: {
        client: 'pg',
        connection: {
            host: 'localhost',
            database: 'congress',
            user: 'username',
        },
        pool: {
            min: 2,
            max: 10
        },
        migrations: {
            tableName: 'knex_migrations'
        }
    },

    production: {
        client: 'postgresql',
        connection: {
            database: 'my_db',
            user: 'username',
            password: 'password'
        },
        pool: {
            min: 2,
            max: 10
        },
        migrations: {
            tableName: 'knex_migrations'
        }
    }

};
