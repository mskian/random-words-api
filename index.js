import express from 'express';
import * as cheerio from 'cheerio';
import cors from 'cors';
import nlp from 'compromise';
import speechPlugin from 'compromise-speech'
nlp.plugin(speechPlugin)
import randomUseragent from 'random-useragent';
import axios from 'axios';
import { rateLimit } from 'express-rate-limit';
import dummydata from './error.js';

const rua = randomUseragent.getRandom();
const app = express();
const port = process.env.PORT || 3000;
var wordOfDay = [];

var allowedOrigins = ['http://localhost:8080',
    'https://words.sanweb.info',
    'https://sanweb.info/'
];

app.use(cors({
    origin: function(origin, callback) {
        if (!origin) return callback(null, true);
        if (allowedOrigins.indexOf(origin) === -1) {
            var msg = 'The CORS policy for this site does not ' +
                'allow access from the specified Origin.';
            //return callback(new Error(msg), false);
             return callback((msg));
        }
        return callback(null, true);
    }
}));

const apiRequestLimiter = rateLimit({
    windowMs: 1 * 60 * 1000,
    max: 40,
    handler: function (req, res) {
        return res.status(429).json(
          dummydata()
        )
    }
})

app.get('/', apiRequestLimiter, function(req, res) {
    res.header('Access-Control-Allow-Headers', 'Access-Control-Allow-Headers,Content-Type,Access-Control-Allow-Methods, Authorization, X-Requested-With');
    res.header('Access-Control-Allow-Methods', 'GET');
    res.header('X-Frame-Options', 'DENY');
    res.header('X-XSS-Protection', '1; mode=block');
    res.header('X-Content-Type-Options', 'nosniff');
    res.header('Strict-Transport-Security', 'max-age=63072000');
    res.setHeader('Content-Type', 'application/json');
    app.disable('x-powered-by');

    axios({
        method: 'GET',
        url: 'https://randomword.com/',
        headers: {
            'User-Agent': rua
        }
    }).then(function(response) {

        const $ = cheerio.load(response.data);

        if (wordOfDay.length > 0) {
            wordOfDay = [];
        }

        var post = $('.section #shared_section');
        var word = post.find('#random_word').eq(0).text().replace('\r\n\t\t\t\t\t', '').replace('\r\n\t\t\t\t', '').replace('\n\t\t\t\t\t', '').replace('\n\t\t\t\t', '');
        var definition = post.find('#random_word_definition').eq(0).text().replace('\n', '');
        var pronounceword = word;
        let doc = nlp(pronounceword);
        var pronounced = doc.terms().soundsLike()
        var pronounce = pronounced;
        wordOfDay.push({
            word: decodeURI(word.charAt(0).toUpperCase() + word.slice(1)),
            definition: decodeURI(definition.charAt(0).toUpperCase() + definition.slice(1)).trim(),
            pronunciation: decodeURI(pronounce)
        })
        res.send(JSON.stringify(wordOfDay, null, 2));

    }).catch(function(error) {
        if (!error.response) {
            res.send(dummydata());
        } else {
            res.send(dummydata());
        }
    });

});

app.get('/api/:word', apiRequestLimiter, function(req, res) {
    res.header('Access-Control-Allow-Headers', 'Access-Control-Allow-Headers,Content-Type,Access-Control-Allow-Methods, Authorization, X-Requested-With');
    res.header('Access-Control-Allow-Methods', 'GET');
    res.header('X-Frame-Options', 'DENY');
    res.header('X-XSS-Protection', '1; mode=block');
    res.header('X-Content-Type-Options', 'nosniff');
    res.header('Strict-Transport-Security', 'max-age=63072000');
    res.setHeader('Content-Type', 'application/json');
    app.disable('x-powered-by');

    var userword = encodeURIComponent(req.params.word) || "Automation";
    let wordData = nlp(userword);
    var pronouncedWord = wordData.terms().soundsLike()
    var getPronounce = decodeURIComponent(pronouncedWord);
    res.status(200).json(getPronounce);

});

app.use('/', function(req, res) {
    res.status(404).json({
        error: 1,
        message: 'Page or Data not Found'
    });
})

app.use((err, req, res, next) => {
    if (!err) return next();
    return res.status(403).json({
        error: 1,
        message: 'Page or Data not Found'
    });
});

app.listen(port, function() {
    console.log('listening on port ' + port);
});