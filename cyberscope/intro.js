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
        game.load.image('171', 'assets/171.png');
        game.load.image('imgHeader', 'assets/header.png');
        game.load.image('imgFooter', 'assets/footer.png');
        game.load.image('midlight', 'assets/midlight-express.gif');
        game.load.bitmapFont('gem', 'assets/gem.png', 'assets/gem.xml');
        game.load.json('contents', 'assets/contents.json');
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
        that.objs["tween"] = game.add.tween(black).to({alpha:0},2000,Phaser.Easing.None,true);
        that.objs["tween"].onComplete.add(function(){
            // game.time.events.add(2000, onCompleteFn, 0, that);
            game.time.events.add(2000, function() {
                that.objs["tween"] = game.add.tween(that.objs['midlight']).to({alpha:0.33},500,Phaser.Easing.None,true);
                that.showTOC();
            });
        });
    },

    showTOC: function() {
        that = this;
        json = game.cache.getJSON('contents');
        console.log(json);
        title = json.articles[0].title;
        text = json.articles[0].body;

        y = TEXT_Y;
        x = TEXT_X;
        width = TEXT_BLOCK_WIDTH;
        space = TEXT_BLOCK_SPACE;
        size = 16;


        that.objs['titleFont'] = game.add.retroFont('171', 16, 18, "ABCDEFGHIJKLMNOPQRSTUVWXYZ| 0123456789*=!ø:.,\\?->=:;+()`", 19, 0, 1);
        that.objs['titleSprite'] = game.add.image(LEFT_BLOCK_X, TITLE_Y, that.objs['titleFont']);
        that.objs['titleFont'].text = title;
        that.objs['titleSprite'].x = -that.objs['titleSprite'].width;


        that.bmpBlockLeft = game.add.bitmapText(game.width, y, 'gem', "loading", size);
        that.bmpBlockLeft.tint = 0xeeddff;
        that.bmpBlockLeft.maxWidth = width;
        that.bmpBlockLeft.text = text;

        that.bmpBlockRight = game.add.bitmapText(game.width + RIGHT_BLOCK_X, y, 'gem', "loading", size);
        that.bmpBlockRight.tint = 0xeeddff;
        that.bmpBlockRight.maxWidth = width;
        that.bmpBlockRight.text = text;

        game.add.tween(that.objs['titleSprite']).to({x:LEFT_BLOCK_X},1000,Phaser.Easing.Cubic.Out,true);
        game.add.tween(that.bmpBlockLeft).to({x:LEFT_BLOCK_X},1000,Phaser.Easing.Cubic.Out,true);
        game.add.tween(that.bmpBlockRight).to({x:RIGHT_BLOCK_X},1000,Phaser.Easing.Cubic.Out,true);

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

        this.fadein(this.showTOC);
/*
        json = game.cache.getJSON('contents');
        console.log(json);
        title = json.articles[0].title;
        text = json.articles[0].body;

        y = TEXT_Y;
        x = TEXT_X;
        width = TEXT_BLOCK_WIDTH;
        space = TEXT_BLOCK_SPACE;
        size = 16;

        that = this;

        this.objs['titleFont'] = game.add.retroFont('171', 16, 18, "ABCDEFGHIJKLMNOPQRSTUVWXYZ| 0123456789*=!ø:.,\\?->=:;+()`", 19, 0, 1);
        this.objs['titleSprite'] = game.add.image(LEFT_BLOCK_X, TITLE_Y, this.objs['titleFont']);
        this.objs['titleFont'].text = title;
        this.objs['titleSprite'].x = -this.objs['titleSprite'].width;


        this.bmpBlockLeft = game.add.bitmapText(game.width, y, 'gem', "loading", size);
        this.bmpBlockLeft.tint = 0xeeddff;
        this.bmpBlockLeft.maxWidth = width;
        this.bmpBlockLeft.text = text;

        this.bmpBlockRight = game.add.bitmapText(game.width + RIGHT_BLOCK_X, y, 'gem', "loading", size);
        this.bmpBlockRight.tint = 0xeeddff;
        this.bmpBlockRight.maxWidth = width;
        this.bmpBlockRight.text = text;

        game.add.tween(this.objs['titleSprite']).to({x:LEFT_BLOCK_X},1000,Phaser.Easing.Cubic.Out,true);
        game.add.tween(this.bmpBlockLeft).to({x:LEFT_BLOCK_X},1000,Phaser.Easing.Cubic.Out,true);
        game.add.tween(this.bmpBlockRight).to({x:RIGHT_BLOCK_X},1000,Phaser.Easing.Cubic.Out,true);

        // add header and footer images
        this.objs['header'] = game.make.bitmapData();
        this.objs['header'].load('imgHeader');
        this.objs['footer'] = game.make.bitmapData();
        this.objs['footer'].load('imgFooter');
        this.objs['sHeader'] = game.add.sprite(0, -this.objs['footer'].height, this.objs['header']);
        this.objs['sFooter'] = game.add.sprite(0, game.height+this.objs['footer'].height, this.objs['footer']);
        game.add.tween(this.objs['sFooter']).to({y:game.height - this.objs['footer'].height},1000,Phaser.Easing.Cubic.Out,true);
        game.add.tween(this.objs['sHeader']).to({y:0},1000,Phaser.Easing.Cubic.Out,true);
*/
    },


    update: function() {
        // Hack for passing the context of this to timeout fn
        var that = this;

    },

};
