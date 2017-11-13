/* ======================== ReaderState ==============================*/
/*  Presents table of contents, and handles article rendering */

var ReaderState = function (game){
    this.bmpTitle = null;
    this.bmpBlockLeft = null;
    this.bmpBlockRight = null;
    this.objs = [];
};

const CINEMASCOPE = 70;
const TITLE_Y = 90;
const TEXT_Y = 130;
const TEXT_X = 20;
const TEXT_BLOCK_SPACE = 20;
const TEXT_BLOCK_WIDTH = 350;
const TEXT_BLOCK_MAX_HEIGHT = 400;
const LEFT_BLOCK_X = TEXT_X;
const RIGHT_BLOCK_X = TEXT_X + TEXT_BLOCK_WIDTH + TEXT_BLOCK_SPACE;
const FONT_SIZE = 16;

ReaderState.prototype = {

    init: function() {

    },

    preload: function() {
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
        that.objs["tween"] = game.add.tween(black).to({alpha:0},1000,Phaser.Easing.None,true);
        that.objs["tween"].onComplete.add(function(){
            // another way: 
            // game.time.events.add(2000, onCompleteFn, 0, that);
            game.time.events.add(2000, function() {
                that.objs["tween"] = game.add.tween(that.objs['midlight']).to({alpha:0.33},1000,Phaser.Easing.None,true);
                that.prepareScreen();
            });
        });
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

    prepareScreen: function() {
        that = this;
        json = game.cache.getJSON('contents');

        that.objs['Articles'] = game.add.group();

        title = json.articles[1].title;
        text = json.articles[1].body; // left text
        text2 = json.articles[0].body2; // right text 
        gfx = json.articles[1].gfx;

        // add header and footer images
        that.objs['header'] = game.make.bitmapData();
        that.objs['header'].load('imgHeader');
        that.objs['footer'] = game.make.bitmapData();
        that.objs['footer'].load('imgFooter');
        that.objs['sHeader'] = game.add.sprite(0, -that.objs['footer'].height, that.objs['header']);
        that.objs['sFooter'] = game.add.sprite(0, game.height+that.objs['footer'].height, that.objs['footer']);
        game.add.tween(that.objs['sFooter']).to({y:game.height - that.objs['footer'].height},1000,Phaser.Easing.Cubic.Out,true);
        game.add.tween(that.objs['sHeader']).to({y:0},1000,Phaser.Easing.Cubic.Out,true);

        game.time.events.add(2000, function() {
            that.showTOC();
        });

        // create TOC and other buttons
        var button = game.add.button(0, 0, 
            'alpha', that.tocOnClick, this, 0, 0, 0);
        button.x = 0; 
        button.y = 0;
        button.width = game.width;
        button.height = CINEMASCOPE;
        button.name = "toc";
        button.inputEnabled = false;
        that.objs.tocButton = button;

        button = game.add.button(0, 0, 
            'alpha', that.pageOnClick, this, 0, 0, 0);
        button.x = TEXT_X; 
        button.y = CINEMASCOPE;
        button.width = TEXT_BLOCK_WIDTH;
        button.height = TEXT_BLOCK_MAX_HEIGHT;
        button.name = "left";
        button.inputEnabled = false;
        that.objs.leftButton = button;

        button = game.add.button(0, 0, 
            'alpha', that.pageOnClick, this, 0, 0, 0);
        button.x = RIGHT_BLOCK_X; 
        button.y = TEXT_Y; 
        button.width = TEXT_BLOCK_WIDTH;
        button.height = TEXT_BLOCK_MAX_HEIGHT;
        button.name = "right";
        button.inputEnabled = false;
        that.objs.rightButton = button;

    },

    showTOC: function() {
        that = this;
        json = game.cache.getJSON('contents');
        var size = FONT_SIZE;
        that.loc = "toc";
        that.objs.tocButton.inputEnabled = false;
        that.objs.leftButton.inputEnabled = false;
        that.objs.rightButton.inputEnabled = false;

        for (i = 0; i < json.articles.length; i++) {
            var article = json.articles[i];
            console.log("article #" + i + ": " + article.title);

            var button = game.add.button(0, 0, 
                'icon', this.actionOnClick, this, 0, 0, 0);
            button.width = 350;
            button.height = 32;
            button.x = TEXT_X;
            button.y = TEXT_Y + i*(button.height * 1.4);
            button.article = article;
            that.objs['Articles'].add(button);

            var text = game.add.bitmapText(TEXT_X + 40 /*fixed icon width*/ + 10, button.y + button.height/2 - size/2, 'gem', article.title, size);
            text.tint = 0xffbb66;
            that.objs['Articles'].add(text);
        }

        that.objs['Articles'].alpha = 0.0;
        game.add.tween(that.objs['Articles']).to({alpha:1.0},1000,Phaser.Easing.Cubic.Out,true);        

        that.objs.slide = game.add.sprite(800-320, 134, 'slide1');
        that.objs.slide.alpha = 0.0;
        game.add.tween(that.objs.slide).to({alpha:1.0},1000,Phaser.Easing.Cubic.Out,true);       
        that.objs.Articles.add(that.objs.slide);
    },

    tocOnClick: function(e) {
        console.log("TOC clicked");
        if (this.loc == "toc")
            return;

        // or hide whatever is being shown
        else if (this.loc == "article")
            this.hideArticle();
        else
            console.log("error: unknown loc " + this.loc);
    },

    actionOnClick: function(e) {
        console.log(e.article.title);
        var tween = game.add.tween(that.objs['Articles']).to({alpha:0.0},1000,Phaser.Easing.Cubic.Out,true);
        that = this;
        tween.onComplete.add(function(){
            console.log("Show article");
            that.showArticle(e.article);
        });

        // evict all TOC elements from memory
        game.time.events.add(1200, function() {
            that.objs['Articles'].forEach(function(item) {
                item.kill();
            });
            that.objs['Articles'].removeAll();
        }
        );

    },

    showArticle: function(article) {
        that = this;
        title = article.title;
        text = article.body; // left text
        gfx = article.gfx;
        that.loc = "article";
        that.objs.tocButton.inputEnabled = true;
        that.objs.leftButton.inputEnabled = true;
        that.objs.rightButton.inputEnabled = true;

        y = TEXT_Y;
        x = TEXT_X;
        width = TEXT_BLOCK_WIDTH;
        space = TEXT_BLOCK_SPACE;
        size = 16;

        that.objs['gfx'] = game.add.image(game.width + RIGHT_BLOCK_X, TEXT_Y, gfx);
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
                var picoffset = 0;
                if (blockid & 1)
                    picoffset = that.objs['gfx'].height + 16;
                if (that.bmpBlockLeft.textHeight < TEXT_BLOCK_MAX_HEIGHT - picoffset) {
                    lastwordbegin = char;
                    if (eot)
                        that.objs['blocks'][blockid++] = text.substring(begin, totalCharsProcessed);
                } else {
                    that.bmpBlockLeft.text = text.substring(begin, lastwordbegin);
                    that.objs['blocks'][blockid++] = text.substring(begin, lastwordbegin);
                    begin = lastwordbegin;
                }

                if (eot) {
                    that.objs['pagesnum'] = Math.floor(blockid/2);
                    that.objs['curpage'] = 0;
                    that.objs['numblocks'] = blockid;
                    break;
                }
            }
        }

        that.bmpBlockLeft.text = that.objs['blocks'][0];

        that.bmpBlockRight = game.add.bitmapText(game.width + RIGHT_BLOCK_X, y + that.objs['gfx'].height + 3, 'gem', "loading", size);
        that.bmpBlockRight.tint = 0xeeddff;
        that.bmpBlockRight.maxWidth = width;
        that.bmpBlockRight.text = that.objs['numblocks']>1 ? that.objs['blocks'][1] : ""
        // for (i=0; i<blockid; i++) {
        //     console.log("=============================");
        //     console.log("BLOCK ID " + i);
        //     console.log("=============================");
        //     console.log(that.objs['blocks'][i]);
        //     console.log("\n\n");
        // }

        console.log("Launching tweens");
        game.add.tween(that.objs['titleSprite']).to({x:LEFT_BLOCK_X},1000,Phaser.Easing.Cubic.Out,true);
        game.add.tween(that.bmpBlockLeft).to({x:LEFT_BLOCK_X},1000,Phaser.Easing.Cubic.Out,true);
        game.add.tween(that.bmpBlockRight).to({x:RIGHT_BLOCK_X},1000,Phaser.Easing.Cubic.Out,true);
        game.add.tween(that.objs['gfx']).to({x:RIGHT_BLOCK_X},1000,Phaser.Easing.Cubic.Out,true);

        // assign listeners for mouse interactions
        game.input.onDown.add(that.pageOnClick, that);
    },

    hideArticle: function() {
        console.log("Hide article begins, launch tweens");
        game.add.tween(that.objs['titleSprite']).to({x:-that.objs['titleSprite'].width},1000,Phaser.Easing.Cubic.Out,true);
        game.add.tween(that.bmpBlockLeft).to({x:game.width},1000,Phaser.Easing.Cubic.Out,true);
        game.add.tween(that.bmpBlockRight).to({x:game.width},1000,Phaser.Easing.Cubic.Out,true);
        var tween = game.add.tween(that.objs['gfx']).to({x:game.width + RIGHT_BLOCK_X},1000,Phaser.Easing.Cubic.Out,true);

        tween.onComplete.add(function(){
            that.showTOC();
        });

        // evict all page elements from memory
        game.time.events.add(1200, function() {
            that.bmpBlockRight.kill();
            that.bmpBlockLeft.kill();
            that.objs['titleSprite'].kill();
            that.objs['gfx'].kill();                    
        }
        );        
    },

    pageOnClick: function(e) {
        var that = this;

        var curpage = that.objs['curpage'];
        var pagesnum = that.objs['pagesnum'];
        var numblocks = that.objs['numblocks'];

        if (e.name == "right") {
                console.log("Pressed NEXT");
            if (curpage < pagesnum) {
                curpage++;
                var lp = curpage*2;
                var rp = lp+1;
                that.bmpBlockLeft.text = that.objs['blocks'][lp];
                if (rp < numblocks)
                    that.bmpBlockRight.text = that.objs['blocks'][rp];
                else
                    that.bmpBlockRight.text = "";
                that.objs['curpage'] = curpage;
            }
        } else if (e.name == "left") {
            console.log("Pressed PREV");
            if (curpage > 0) {
                curpage--;
                var lp = curpage*2;
                var rp = lp+1;
                that.bmpBlockLeft.text = that.objs['blocks'][lp];
                that.bmpBlockRight.text = that.objs['blocks'][rp];
                that.objs['curpage'] = curpage;
            }
        }
    }
};
