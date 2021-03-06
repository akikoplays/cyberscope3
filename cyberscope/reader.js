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

class Temp {
    constructor(str) {
        this._name = str;
    }

    tell() {
        console.log(this._name);
    }
}

ReaderState.prototype = {

    init: function() {
    },

    preload: function() {
        let tmp = new Temp("Deffard");
        console.log("######");
        tmp.tell();


        // parse articles
        json = game.cache.getJSON('contents');
        console.log("contents json loaded: " + json);
        for (i = 0; i < json.articles.length; i++) {
            gfx = json.articles[i].gfx;
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
            'icon', this.articleOnClick, this, 0, 0, 0);
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

        that.objs.slide = game.add.sprite(800, 134, 'slide1');
        that.objs.slide.alpha = 0.0;
        game.add.tween(that.objs.slide).to({alpha:1.0},1000,Phaser.Easing.Cubic.Out,true);
        var tween = game.add.tween(that.objs.slide).to({x:800-320+40},1500,Phaser.Easing.Cubic.Out,true);
        that.objs.Articles.add(that.objs.slide);

        tween.onComplete.add(function(){
            that.objs.logger = new Logger(that);
            that.objs.logger.start();
        });
    },

    // Callback when TOC button is clicked.
    // Decides what to hide in order to show TOC.
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

    // Callback that handles article selection from the TOC.
    // Cleanes up TOC display list, releases its resources and animates selected article into view.
    articleOnClick: function(e) {
        console.log(e.article.title);
        var tween = game.add.tween(that.objs['Articles']).to({alpha:0.0},1000,Phaser.Easing.Cubic.Out,true);
        that = this;
        tween.onComplete.add(function(){
            console.log("Show article");
            that.showArticle(e.article);
        });

        // evict all TOC elements from memory
        game.time.events.add(1200, function() {
            that.objs.Articles.forEach(function(item) {
                item.kill();
            });
            that.objs.Articles.removeAll();
        }
        );

    },

    // Central function, assembles the page & gfx based on selected article data.
    // Note: you have to call hideArticle() to properly close it.
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

        // show page indicator
        that.objs.indicator = new Indicator(that);
        that.objs.indicator.setup(RIGHT_BLOCK_X+TEXT_BLOCK_WIDTH, TEXT_Y+TEXT_BLOCK_MAX_HEIGHT, 
            6, 4, that.objs.pagesnum);
        that.objs.indicator.setStep(0);

    },

    // Disassembles pages and gfx, releasing resources in the end
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
        that.objs.indicator.kill();
        game.time.events.add(1200, function() {
            that.bmpBlockRight.kill();
            that.bmpBlockLeft.kill();
            that.objs['titleSprite'].kill();
            that.objs['gfx'].kill();
        }
        );
    },

    // Callback that handles left/right page clicks
    pageOnClick: function(e) {
        var that = this;

        var curpage = that.objs['curpage'];
        var pagesnum = that.objs['pagesnum'];
        var numblocks = that.objs['numblocks'];

        if (e.name == "right") {
                console.log("Pressed NEXT");
            if (curpage < pagesnum) {
                curpage++;
                that.objs.indicator.setStep(curpage);
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
                that.objs.indicator.setStep(curpage);
                var lp = curpage*2;
                var rp = lp+1;
                that.bmpBlockLeft.text = that.objs['blocks'][lp];
                that.bmpBlockRight.text = that.objs['blocks'][rp];
                that.objs['curpage'] = curpage;
            }
        }
    }
};

Logger = function(parent){
    this.x = 0;
    this.y = 0;
    this.tail = 0;
    this.parent = parent;
    this.text = "It is a rainy day. I hear construction workers\npounding on concrete, the floor above. I wonder how\nmuch light is necessary to keep me awake, the\ntungsten fog seems to lack shadows, if I don't see\nshadows, I easily fall asleep. ";
    this.showText = "";
    this.cur = 0;
    this.obj = game.add.bitmapText(parent.objs.slide.x, parent.objs.slide.y+parent.objs.slide.height, 
        'gem', this.showText, 12);
    this.obj.maxWidth = parent.objs.slide.width;

    this.cursor = game.add.graphics(this.obj.x, this.obj.y+2);
    this.cursor.beginFill(0xffffff);
    this.cursor.alpha = 1;
    this.cursor.drawRect(0, 0,
        10, 10);
    this.cursor.endFill();
    this.cursor.cnt = 0;
};

Logger.prototype = {


  start: function() {
    var that = this;
    game.time.events.repeat(20, that.text.length, that.typeIt, that);
    this.parent.objs.Articles.add(this.obj);
    this.parent.objs.Articles.add(this.cursor);
    game.time.events.repeat(20, 1000000, that.cursorBlink, that);
  },

  update: function() {
    var that = this;
  },

  typeIt: function() {
    var ch = this.text[this.tail++];
    this.showText += ch;
    this.obj.text = this.showText;
    if (ch == '\n') this.newline = true;
  },

  cursorBlink: function() {
    this.cursor.x = this.obj.x + this.cursor.cnt*(8*0.75);
    if (this.showText.length < this.text.length)
        this.cursor.cnt++;
    if (this.newline) {
        this.cursor.cnt = 0;
        this.cursor.y += 16*0.75;
        this.newline = false;
    }
    this.cursor.alpha = this.cursor.alpha == 1 ? this.cursor.alpha = 0 : this.cursor.alpha = 1;
  }

};

Indicator = function(parent) {
    this.numBlocks = 0;
};

Indicator.prototype = {
    setup: function(x, y, size, spacing, numBlocks) {
        this.numBlocks = numBlocks;
        this.curBlock = 0;
        this.x = x;
        this.y = y;
        this.spacing = spacing;
        this.size = size;
        this.current = 0;
        this.osc = 0;

        this.blocks = game.add.graphics(this.x, this.y);
        console.log("Setting up " + this.numBlocks);

        var that = this;
        that.blinkEvt = game.time.events.repeat(100, 1000000, that.updateGfx, that);
    },

    kill() {
        game.time.events.remove(that.blinkEvt);
        this.blocks.kill();        
    },

    setStep: function(idx) {
        this.current = idx;
    },

    updateGfx: function() {
        this.blocks.clear();
        for (i=this.numBlocks; i>=0; i--) {

            if (this.current == (this.numBlocks-i) && (this.osc++ & 1)) 
                this.blocks.beginFill(0xffffff);
            else 
                this.blocks.lineStyle(2, 0xffffff, 1);            
            this.blocks.drawRect(-i*this.size - i*this.spacing, 0, this.size, this.size);
            if (this.current == this.numBlocks-i) 
                this.blocks.endFill();
        }        
        this.blocks.tint = 0xaabbff;
    }


};