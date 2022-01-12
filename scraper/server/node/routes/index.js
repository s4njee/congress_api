var express = require('express');
var router = express.Router();
const knex = require('knex')({
  client: 'pg',
  connection: {
    host : 'db',
    user : 'postgres',
    password : 'postgres',
    database : 'postgres'
  }
});
/* GET home page. */
router.get('/', async function(req, res, next) {
  res.render('index', { title: 'Express' });
  try {
    await sequelize.authenticate();
    console.log('Connection has been established successfully.');
  } catch (error) {
    console.error('Unable to connect to the database:', error);
  }
});

router.post('/temp_upload', function (req, res) {
  knex('temps').insert({sensor: req.body.sensor, date: new Date().toLocaleString(), temp_f: req.body.temp_f, temp_c: req.body.temp_c})
      .then( function (result) {
        res.json({ success: true, message: 'ok' });     // respond back to request
      })
})   


module.exports = router;
