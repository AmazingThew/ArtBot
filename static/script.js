"use strict";


function getScrollbarWidth() { //BURN WEB STANDARDS TO THE GROUND
    var inner = document.createElement('p');
    inner.style.width = "100%";
    inner.style.height = "200px";

    var outer = document.createElement('div');
    outer.style.position = "absolute";
    outer.style.top = "0px";
    outer.style.left = "0px";
    outer.style.visibility = "hidden";
    outer.style.width = "200px";
    outer.style.height = "150px";
    outer.style.overflow = "hidden";
    outer.appendChild(inner);

    document.body.appendChild(outer);
    var w1 = inner.offsetWidth;
    outer.style.overflow = 'scroll';
    var w2 = inner.offsetWidth;
    if (w1 == w2) w2 = outer.clientWidth;

    document.body.removeChild(outer);

    return (w1 - w2);
}

var scrollbarWidth = getScrollbarWidth();


var ArtColumn = React.createClass({
    getInitialState: function() {
        return {
            artArray: [],
            progress: 0,
            intervalId: 0
        };
    },

    updateProgress: function() {
        if (this.state.progress < 100) {
            this.setState({progress: this.state.progress + 1});
        } else {
            console.log('Clearing interval: ' + this.state.intervalId);
            window.clearInterval(this.state.intervalId);
            this.loadArt();
        }
    },

    loadArt: function() {
        console.log('STARTING LOAD')
        $.ajax({
            url: this.props.url,
            dataType: 'json',
            cache: false,
            success: function(data) {
                this.setState({
                    artArray: data,
                    progress: 0,
                    intervalId: window.setInterval(this.updateProgress, 1200)
                });
                console.log('FINISHED LOAD')
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, xhr.responseText);
                if (xhr.status === 401) {
                    window.location.replace('/authorizeDeviantart')
                }
            }.bind(this)
        });
    },

    componentDidMount: function() {
        this.loadArt();
    },

    render: function() {
        return (
            <div className="artColumn">
                <div className='progressBar' style={{height: 100 - this.state.progress + '%'}}></div>
                <ArtList artArray={this.state.artArray} />
            </div>
        );
    }
});



var ArtList = React.createClass( {
    render: function() {
        var artNodes = this.props.artArray.map(function (art) {
            return (
                <Art key={art.identifier} artData={art} />
            );
        });
        return (
            <div className="artList">
                {artNodes}
            </div>
        );
    }
});


//Percentages of viewport width
var artPadding = 1;
var artMargin = 1;
var artBorderRadius = 1;
var infoBarHeight = 5;
var infoBarPadding = 1;
//Pixels
var artBorderWidth = 2;

function calculateDimensions(baseImageWidth, baseImageHeight, name) {
    var ww = window.innerWidth - scrollbarWidth*2;
    var wh = window.innerHeight;
    var vMin = (ww < wh) ? ww : wh;

    baseImageWidth  = parseInt(baseImageWidth, 10)
    baseImageHeight = parseInt(baseImageHeight, 10)

    var scale = Math.min(
        (ww - ((vMin*artPadding/100.0 + vMin*artMargin/100.0 + artBorderWidth) * 2.0))/baseImageWidth,
        (wh -  (vMin*artPadding/100.0 + vMin*artMargin/100.0 + artBorderWidth) * 2.0 - vMin*infoBarHeight/100.0 - 2.0*vMin*infoBarPadding/100.0)/baseImageHeight
    );

    return {
        targetWidth  : baseImageWidth*scale,
        targetHeight : baseImageHeight*scale,
    };
}

var Art = React.createClass( {
    getInitialState: function() {
        var state = calculateDimensions(this.props.artData.width, this.props.artData.height, this.props.artData.imageTitle);
        state.hidden = false;
        return state;
    },

    handleResize: function(e) {
        this.setState(calculateDimensions(this.props.artData.width, this.props.artData.height, this.props.artData.imageTitle));
    },

    componentDidMount: function() {
        window.addEventListener('resize', this.handleResize);
    },

    handleClick: function(event) {
        event.preventDefault();
        this.setState({hidden: !this.state.hidden})
    },

    render: function() {
        var targetWidth  = this.state.targetWidth;
        var targetHeight = this.state.targetHeight;

        var images = this.props.artData.imageUrls.map(function (url) {
            return (
                <a href={url} key={url}><img src={url} alt={url} style={{height: targetHeight, width: targetWidth}} /></a>
            );
        });

        var artStyle = {
            margin: artMargin.toString()+'vmin',
            borderRadius: artBorderRadius.toString()+'vmin',
            border: artBorderWidth.toString()+'px solid',
        };

        var artHolderStyle = {
            display: (this.state.hidden) ? 'none' : 'inline-block',
            padding: artPadding.toString()+'vmin'
        };

        var infoBarStyle = {
            height: infoBarHeight.toString()+'vmin',
            /*backgroundColor: '#3f292f',*/
            padding: infoBarPadding.toString()+'vmin'
        };

        return (
            <div className="art" style={artStyle}>
                <div className="artHolder" style={artHolderStyle}>
                    {images}
                </div>
                <div className="infoBar" style={infoBarStyle}>
                    <a href={this.props.artData.profileUrl}><img src={this.props.artData.authorAvatarUrl} /></a>
                    <div className="nameHolder" style={{marginLeft: infoBarPadding.toString()+'vmin'}}>
                        <p>
                            <a href={this.props.artData.profileUrl}>{this.props.artData.authorName}</a>
                            <br/>
                            {this.props.artData.website}
                        </p>
                    </div>
                    <div className="titleHolder">
                        <h1><a href={this.props.artData.imagePageUrl}>{this.props.artData.imageTitle}</a></h1>
                    </div>
                    <div className="buttonHolder">
                        <a href="#" className="butt" onClick={this.handleClick}>=</a>
                    </div>
                </div>
            </div>
        );
    }
});



//var Art = React.createClass( {
//    render: function() {
//        return (
//            <div className="art">
//            </div>
//        );
//    }
//});

var downReleased = true;
var upReleased   = true;

document.onkeydown = function(e) {
    var ww = window.innerWidth - scrollbarWidth*2;
    var wh = window.innerHeight;
    var vMin = (ww < wh) ? ww : wh;
    var pad = vMin*artMargin/100.0;
    var target;
    var lastTarget;
    //UP
    if (e.keyCode == 38){
        e.preventDefault();
        if (upReleased) {
            $(".art").each(function(i, element) {
                target = $(element).offset().top - pad;
                if (lastTarget + 10 < $(document).scrollTop() && target + 10 > $(document).scrollTop()) {
                    target = lastTarget;
                    return false; // break
                }
                lastTarget = target;
            });
            if (target < $(document).scrollTop()) {
                $("html, body").animate({scrollTop: target}, 200);
            }
            upReleased = false;
        }
    }
    //DOWN
    if (e.keyCode == 40) {
        e.preventDefault();
        if (downReleased) {
            $(".art").each(function(i, element) {
                target = $(element).offset().top - pad;
                if (target - 10 > $(document).scrollTop()) {
                    return false; // break
                }
            });
            $("html, body").animate({scrollTop: target}, 200);
            downReleased = false;
        }
    }
};

document.onkeyup = function(e) {
    var target;
    //UP
    if (e.keyCode == 38){
        upReleased = true;
    }
    //DOWN
    if (e.keyCode == 40) {
        downReleased = true;
    }
};


ReactDOM.render(
  <ArtColumn url="/getWorks" />,
  document.getElementById('EVETHRYING')
);