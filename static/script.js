"use strict";


/*var HideButton = React.createClass({
  getInitialState: function() {
    return {hidden: false};
  },
  handleClick: function(event) {
    this.setState({hidden: !this.state.liked});
  },
  render: function() {
    var text = this.state.liked ? 'like' : 'haven\'t liked';
    return (
      <p onClick={this.handleClick}>
        You {text} this. Click to toggle.
      </p>
    );
  }
});

ReactDOM.render(
  <LikeButton />,
  document.getElementById('example')
);*/




var ArtColumn = React.createClass({
    getInitialState: function() {
        return {artArray: []};
    },

    loadArt: function() {
        $.ajax({
            url: this.props.url,
            dataType: 'json',
            cache: false,
            success: function(data) {
                this.setState({artArray: data});
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
    var scrollbarWidth = (window.innerWidth-$(window).width());
    var ww = window.innerWidth - scrollbarWidth*2;
    var wh = window.innerHeight;
    var vMin = (ww < wh) ? ww : wh;

    baseImageWidth  = parseInt(baseImageWidth, 10)
    baseImageHeight = parseInt(baseImageHeight, 10)

    var scale = Math.min(
        (ww - ((vMin*artPadding/100.0 + vMin*artMargin/100.0 + artBorderWidth) * 2.0))/baseImageWidth,
        (wh -  (vMin*artPadding/100.0 + vMin*artMargin/100.0 + artBorderWidth) * 2.0 - vMin*infoBarHeight/100.0)/baseImageHeight
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
        console.log(this.state.hidden);
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
                        <h1><a href={this.props.artData.profileUrl}>{this.props.artData.imageTitle}</a></h1>
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



ReactDOM.render(
  <ArtColumn url="/getWorks" />,
  document.getElementById('EVETHRYING')
);