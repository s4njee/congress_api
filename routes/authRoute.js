const oauthPlugin = require("@fastify/oauth2");
const db = require("../controllers/db");

module.exports = async function (fastify, opts) {
  fastify.register(oauthPlugin, {
    name: "googleOAuth2",
    scope: ["profile", "email"],
    credentials: {
      client: {
        id: "292558360958-eiio27t9c3gikshfm6pa4khvunb0d2ff.apps.googleusercontent.com",
        secret: "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",
      },
      auth: oauthPlugin.GOOGLE_CONFIGURATION,
    },
    startRedirectPath: "/login/google",
    callbackUri: "http://localhost:3000/login/google/callback",
    callbackUriParams: {
      // custom query param that will be passed to callbackUri
      access_type: "offline", // will tell Google to send a refreshToken too
    },
  });
  fastify.post("/login", function (request, reply) {
    console.log(JSON.parse(request.body));
    // this.googleOAuth2.getAccessTokenFromAuthorizationCodeFlow(
    //   request,
    //   (err, result) => {
    //     if (err) {
    //       reply.send(err);
    //       return;
    //     }
    credential = JSON.parse(request.body).credential;
    console.log("Bearer " + credential);
    var token = "";
    var email = "";
    fetch("https://www.googleapis.com/oauth2/v2/userinfo", {
      headers: {
        Authorization: "Bearer " + credential,
      },
    })
      .then((res) => res.json())
      .then((json) => {
        console.log(json);
        db.knex
          .raw("select exists(select 1 from users where email= ? )", json.email)
          .then((rows) => {
            if (rows.rows[0].exists == false) {
              db.knex("users")
                .insert({
                  email: json.email,
                  firstname: json.given_name,
                  lastname: json.family_name,
                })
                .then((result) => {
                  console.log(result);
                });
            }
          });
        token = fastify.jwt.sign({ email: json.email });
        email = json.email;
        console.log(token);
        return JSON.stringify({ user: json.email, token: token });
      })
      .then((json) => {
        reply.send(json);
      });
  });
};
