var express = require('express');
var router = express.Router();
const knex = require('knex')({
    client: 'pg',
    connection: {
        connectionString: `postgresql://postgres:postgres@db:5432/csearch`,
        ssl: false
    }
    ,
});

/* GET home page. */
router.get('/', function (req, res, next) {
    res.render('index', {title: 'Express'});
});

router.get('/latest/:type', (req, res) => {
    const data = knex.select(
        'short_title', 'official_title', 'introduced_at', 'summary',
        'actions', 'bill_type', 'congress', 'number',
        'sponsors', 'cosponsors', 'status_at'
    ).from('bills')
        .where({'bill_type':`${req.params.type}`})
        .orderBy('status_at', 'desc').limit(100).then((results) => {
            res.json(results)
        })
});

router.get('/search/:table', (req, res) => {
        try {
            if (req.query.sfilter.toString() === 'relevance') {
                const data = knex.select('short_title', 'official_title', 'introduced_at', 'summary',
                    'actions', 'bill_type', 'congress', 'number',
                    'sponsors', 'cosponsors', 'status_at')
                    .from('bills')
                    .where({'bill_type':`${req.params.table}`})
                    .whereRaw(`${req.params.table}_ts @@ phraseto_tsquery('english', ?)`, req.query.query.toString())
                    .orderByRaw(`ts_rank(${req.params.table}_ts, phraseto_tsquery(?)) desc`, req.query.query.toString())
                    .then(results => {
                        if (results.length <= 100) {
                            res.json(results)
                        } else {
                            res.json(results.slice(0, 100))
                        }
                    })
            } else if (req.query.sfilter.toString() === 'date') {
                const data = knex.select('short_title', 'official_title', 'introduced_at', 'summary',
                    'actions', 'bill_type', 'congress', 'number',
                    'sponsors', 'cosponsors', 'status_at')
                    .from('bills')
			.where({'bill_type':`${req.params.table}`})
			    .whereRaw(`${req.params.table}_ts @@ phraseto_tsquery('english', ?)`, req.query.query.toString())
                    .orderBy('introduced_at', 'desc')
                    .then((results) => {
                        if (results.length <= 100) {
                            res.json(results)
                        } else {
                            res.json(results.slice(0, 100))
                        }
                    })
            }
        } catch (e) {
            console.log(e)
        }
    }
)
module.exports = router;
