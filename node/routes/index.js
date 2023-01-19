var express = require('express');
var router = express.Router();
const knex = require('knex')({
    client: 'pg',
    connection: {
        connectionString: `postgresql://postgres:postgres@postgres-service:5432/csearch`,
        ssl: false
    }
    ,
});
const select_bill = knex.select('shorttitle', 'officialtitle', 'introducedat', 'summary',
'actions', 'billtype', 'congress', 'billnumber',
'sponsors', 'cosponsors', 'statusat')

/* GET home page. */
router.get('/', function (req, res, next) {
    res.render('index', {title: 'Express'});
});

router.get('/latest/:type', (req, res) => {
    const data = knex.select(
        'shorttitle', 'officialtitle', 'introducedat', 'summary',
        'actions', 'billtype', 'congress', 'billnumber',
        'sponsors', 'cosponsors', 'statusat'
    ).from('bills')
        .whereRaw('statusat::date between current_date - 365 and current_date')
        .where({'billtype':`${req.params.type}`})
        .orderBy('statusat', 'desc').limit(100).then((results) => {
            res.json(results)
        })
});

router.get('/search/:table', (req, res) => {
        try {
            if (req.query.sfilter.toString() === 'relevance') {
                const data = select_bill
                    .from('bills')
                    .where({'billtype':`${req.params.table}`})
                    .whereRaw(`${req.params.table}_ts @@ phraseto_tsquery('english', ?)`, req.query.query.toString())
                    .orderByRaw(`ts_rank(${req.params.table}_ts, phraseto_tsquery(?)) desc`, req.query.query.toString())
                    .then(results => {
                        if (results.length <= 100) {
                            res.json(results)
                        } else {
                            res.json(results.slice(0, 100))
                        }
                    })
            } else if (req.query.sfilter.toString() === 'asc') {
                console.log('asc func')
                const data = select_bill
                    .from('bills')
			        .where({'billtype':`${req.params.table}`})
			        .whereRaw(`${req.params.table}_ts @@ phraseto_tsquery('english', ?)`, req.query.query.toString())
                    .orderBy('introducedat', 'asc')
                    .then((results) => {
                        if (results.length <= 100) {
                            res.json(results)
                        } else {
                            res.json(results.slice(0, 100))
                        }
                    })
            }else if (req.query.sfilter.toString() === 'desc') {
                console.log('desc func')
                const data = select_bill
                    .from('bills')
			        .where({'billtype':`${req.params.table}`})
			        .whereRaw(`${req.params.table}_ts @@ phraseto_tsquery('english', ?)`, req.query.query.toString())
                    .orderBy('introducedat', 'desc')
                    .then((results) => {
                        if (results.length <= 100) {
                            res.json(results)
                        } else {
                            res.json(results.slice(0, 100))
                        }
                    })
        } 
    }catch (e) {
            console.log(e)
        }
    }
)
module.exports = router;
