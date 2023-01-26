const db = require('../controllers/db')
const select_bill = db.knex.select('shorttitle', 'officialtitle', 'introducedat', 'summary',
    'actions', 'billtype', 'congress', 'billnumber',
    'sponsors', 'cosponsors', 'statusat')

module.exports = async function(fastify, opts){
    fastify.get('/search/:table', (request,reply)=>{
        console.log(request.query)
        const table = request.params.table
        const query = request.query.query
        select_bill
            .from('bills')
            .where({'billtype':table})
            .whereRaw(`${table}_ts @@ phraseto_tsquery('english', ?)`, query)
            .orderByRaw(`ts_rank(${table}_ts, phraseto_tsquery(?)) desc`, query)
            .limit(30)
            .then(results => {
                reply.send(results)
            })
    })
}
