const { req } = require('pino-std-serializers')
const db = require('../controllers/db')
module.exports = async function(fastify, opts){
    fastify.get('/search/:table/:filter', (request,reply)=>{
        const table = request.params.table
        const query = request.query.query
        const filter = request.params.filter
        if (filter == 'relevance'){
            db.knex.select('billid', 'shorttitle', 'officialtitle', 'introducedat', 'summary',
            'actions', 'billtype', 'congress', 'billnumber',
            'sponsors', 'cosponsors', 'statusat')
            .from('bills')
            .where({'billtype':table})
            .whereRaw(`${table}_ts @@ phraseto_tsquery('english', ?)`, query)
            .orderByRaw(`ts_rank(${table}_ts, phraseto_tsquery(?)) desc`, query)
            .limit(30)
            .then(results => {
                reply.send(results)
            })
        }
        else if (filter == 'date'){
            console.log('date filter selected')
            db.knex.select('billid', 'shorttitle', 'officialtitle', 'introducedat', 'summary',
            'actions', 'billtype', 'congress', 'billnumber',
            'sponsors', 'cosponsors', 'statusat')
            .from('bills')
            .where({'billtype':table})
            .whereRaw(`${table}_ts @@ phraseto_tsquery('english', ?)`, query)
            .orderBy('statusat', 'desc')
            .limit(30)
            .then(results => {
                reply.send(results)
            })
        }
    })
}
