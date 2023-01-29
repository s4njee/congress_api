const db = require('../controllers/db')

module.exports = async function(fastify, opts){
    fastify.get('/latest/:billtype', (request,reply)=>{
        db.knex.select(
            'billid', 'shorttitle', 'officialtitle', 'introducedat', 'summary',
            'actions', 'billtype', 'congress', 'billnumber',
            'sponsors', 'cosponsors', 'statusat'
        ).from('bills')
            .whereRaw('statusat::date between current_date - 365 and current_date')
            .where({'billtype': `${request.params.billtype}`})
            .orderBy('statusat', 'desc').limit(100).then((results) => {
            console.log(results)
            reply.send(results)
        })
    })
}
