import * as cheerio from 'cheerio';
import nlp from 'compromise';
import speechPlugin from 'compromise-speech'
nlp.plugin(speechPlugin)
import randomUseragent from 'random-useragent';
import axios from 'axios';
import dummydata from './error.js';

const rua = randomUseragent.getRandom();
var wordOfDay = [];

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
            definition: decodeURI(definition.charAt(0).toUpperCase() + definition.slice(1)),
            pronunciation: decodeURI(pronounce)
        })
        console.log(wordOfDay);

    }).catch(function(error) {
        if (!error.response) {
            console.log(dummydata());
        } else {
            console.log(dummydata());
        }
    });