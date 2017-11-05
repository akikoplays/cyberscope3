/* ======================== BootState ==============================*/
/*  loads starting screen, shows some blitter image fx and gives control
    to the content table of contents */

var IntroState = function (game){
    this.bmpTitle = null;
    this.bmpBlockLeft = null;
    this.bmpBlockRight = null;
    this.objs = [];
};

const CINEMASCOPE = 70;
const TITLE_Y = 100;
const TEXT_Y = 130;
const TEXT_X = 20;
const TEXT_BLOCK_SPACE = 20;
const TEXT_BLOCK_WIDTH = 350;
const LEFT_BLOCK_X = TEXT_X;
const RIGHT_BLOCK_X = TEXT_X + TEXT_BLOCK_WIDTH + TEXT_BLOCK_SPACE;

IntroState.prototype = {

    init: function() {

    },

    preload: function() {

        // game.load.image('titlescreen', 'assets/cyberscope.jpeg');
        // game.load.image('midlight', 'assets/midlight-express.gif');
        // game.load.image('kickstart', 'assets/kickstart30.gif');
        // game.load.image('floppy', 'assets/floppy.png');
        // game.load.bitmapFont('gem', 'assets/gem.png', 'assets/gem.xml');
        // game.load.script('protracker', 'protracker.js');
        // game.load.binary('mod', 'assets/intermediate.mod', this.modLoaded, this);
        // game.load.json('contents', 'assets/contents.json');
        // game.load.image('171', 'assets/171.png');
        // game.load.image('imgHeader', 'assets/header.png');
        // game.load.image('imgFooter', 'assets/footer.png');
        // game.load.bitmapFont('gem', 'assets/gem.png', 'assets/gem.xml');

        // parse articles
        json = game.cache.getJSON('contents');
        console.log("contents json loaded: " + json);
        for (i = 0; i < json.articles.length; i++) {
            title = json.articles[i].title;
            text = json.articles[i].body;
            gfx = json.articles[i].gfx;
            console.log(title + ", " + text + ", " + gfx);

            game.load.image(gfx, 'assets/' + gfx);
            console.log('loading: ' + 'assets/' + gfx);
        }

    },

    fadein: function(onCompleteFn) {
        that = this;

        var sprite = game.add.sprite(0, CINEMASCOPE, "midlight");
        that.objs["midlight"] = sprite;

        var black = game.add.graphics(0, 0);
        black.beginFill(0x000000);
        black.alpha = 1;
        black.drawRect(0, 0, 
            game.width, game.height);
        black.endFill();
        that.objs["black"] = black;
        that.objs["tween"] = game.add.tween(black).to({alpha:0},100,Phaser.Easing.None,true);
        that.objs["tween"].onComplete.add(function(){
            // another way: 
            // game.time.events.add(2000, onCompleteFn, 0, that);
            game.time.events.add(100, function() {
                that.objs["tween"] = game.add.tween(that.objs['midlight']).to({alpha:0.33},500,Phaser.Easing.None,true);
                that.showTOC();
            });
        });
    },

    showTOC: function() {
        that = this;
        json = game.cache.getJSON('contents');
        console.log(json);
        title = json.articles[1].title;
        text = json.articles[1].body; // left text
        text2 = json.articles[0].body2; // right text 
        gfx = json.articles[1].gfx;

        y = TEXT_Y;
        x = TEXT_X;
        width = TEXT_BLOCK_WIDTH;
        space = TEXT_BLOCK_SPACE;
        size = 16;

        that.objs['gfx'] = game.add.image(game.width + RIGHT_BLOCK_X, TEXT_Y - 30, gfx);
        that.objs['titleSprite'] = game.add.image(LEFT_BLOCK_X, TITLE_Y, that.objs['titleFont']);
        that.objs['titleFont'].text = title;
        that.objs['titleSprite'].x = -that.objs['titleSprite'].width;

        that.bmpBlockLeft = game.add.bitmapText(game.width, y, 'gem', "loading", size);
        that.bmpBlockLeft.tint = 0xeeddff;
        that.bmpBlockLeft.maxWidth = width;

        // break text
        var blockid = 0;
        var totalCharsProcessed = 0;
        var begin = 0;
        var eot = false;
        that.objs['blocks'] = {};
        var lastword = 0;
        while (!eot) {
            
            var char = begin;
            var lastwordbegin = char;

            // isolate block
            while(1){

                // fetch next word
                while(1) {
                    char++;
                    totalCharsProcessed++;

                    // always capture end of text
                    if (totalCharsProcessed >= text.length) {
                        eot = true;
                        break;
                    }
                    if (text[char] == ' ' || text[char] == '.' || text[char] == '\n')
                        break;
                }
                
                that.bmpBlockLeft.text = text.substring(begin, char);

                if (that.bmpBlockLeft.textHeight < 368+16) {
                    //console.log("Text: " + that.bmpBlockLeft.width + ", " + that.bmpBlockLeft.textHeight + ": " + text.substring(begin, char));
                    lastwordbegin = char;

                    if (eot)
                        that.objs['blocks'][blockid++] = text.substring(begin, totalCharsProcessed);

                } else {
                    that.bmpBlockLeft.text = text.substring(begin, lastwordbegin);
                    that.objs['blocks'][blockid++] = text.substring(begin, lastwordbegin);

                    begin = lastwordbegin;
                }

                if (eot)
                    break;
            }
        }

        that.bmpBlockLeft.text = that.objs['blocks'][0];

        that.bmpBlockRight = game.add.bitmapText(game.width + RIGHT_BLOCK_X, y + that.objs['gfx'].height - 26, 'gem', "loading", size);
        that.bmpBlockRight.tint = 0xeeddff;
        that.bmpBlockRight.maxWidth = width;
        that.bmpBlockRight.text = that.objs['blocks'][1];//text2;
        for (i=0; i<blockid; i++) {
            console.log("=============================");
            console.log("BLOCK ID " + i);
            console.log("=============================");
            console.log(that.objs['blocks'][i]);
            console.log("\n\n");
        }

        game.add.tween(that.objs['titleSprite']).to({x:LEFT_BLOCK_X},1000,Phaser.Easing.Cubic.Out,true);
        game.add.tween(that.bmpBlockLeft).to({x:LEFT_BLOCK_X},1000,Phaser.Easing.Cubic.Out,true);
        game.add.tween(that.bmpBlockRight).to({x:RIGHT_BLOCK_X},1000,Phaser.Easing.Cubic.Out,true);
        game.add.tween(that.objs['gfx']).to({x:RIGHT_BLOCK_X},1000,Phaser.Easing.Cubic.Out,true);

        // add header and footer images
        that.objs['header'] = game.make.bitmapData();
        that.objs['header'].load('imgHeader');
        that.objs['footer'] = game.make.bitmapData();
        that.objs['footer'].load('imgFooter');
        that.objs['sHeader'] = game.add.sprite(0, -that.objs['footer'].height, that.objs['header']);
        that.objs['sFooter'] = game.add.sprite(0, game.height+that.objs['footer'].height, that.objs['footer']);
        game.add.tween(that.objs['sFooter']).to({y:game.height - that.objs['footer'].height},1000,Phaser.Easing.Cubic.Out,true);
        game.add.tween(that.objs['sHeader']).to({y:0},1000,Phaser.Easing.Cubic.Out,true);
    },

    create: function() {

        
        console.log("midlight check: " + game.cache.checkImageKey('midlight'));

        game.stage.backgroundColor = "#200000";
        game.stage.smoothed = false;

        this.objs['titleFont'] = game.add.retroFont('171', 16, 18, "ABCDEFGHIJKLMNOPQRSTUVWXYZ| 0123456789*=!ø:.,\\?->=:;+()`", 19, 0, 1);

        this.fadein(this.showTOC);
    },


    update: function() {
        // Hack for passing the context of this to timeout fn
        var that = this;

    },

};
