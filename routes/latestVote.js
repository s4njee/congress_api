const db = require("../controllers/db");

module.exports = async function (fastify, opts) {
  fastify.get("/latestv/:chamber", (request, reply) => {
    db.knex
      .select(
        "congress",
        "votenumber",
        "votedate",
        "question",
        "result",
        "chamber",
        "votetype",
        "voteid",
        "yea",
        "nay",
        "present",
        "notvoting"
      )
      .from("votes")
      .whereRaw("votedate::date between current_date - 365 and current_date")
      .where({ chamber: `${request.params.chamber}` })
      .orderBy("votedate", "desc")
      .limit(30)
      .then((results) => {
        console.log(results);
        reply.send(results);
      });
  });
};
