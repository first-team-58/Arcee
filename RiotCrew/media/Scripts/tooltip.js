(function ($){
	var settings = {
		tooltip: '',
		css: '',
		xOffset: 5,
		yOffset: 20
	},
	structure = '<div class="tooltip ui-state-default ui-helper-reset ui-state-active ui-corner-all ___EXTRA_CSS___">___CONTENT___</div>';
	$.fn.tooltip = function(options){
		var opts;
		opts = $.extend({}, settings);
		if (typeof options === 'string' || typeof options === 'function'){
			opts.tooltip = options;
		} else if (typeof options === 'string'){
			$.extend(opts, options);
		} 
		return this.each(
			function(e){
				$(this).hover(function(e){
					var css = (typeof opts.css === 'function')? opts.css(this): opts.css, 
					tooltip = (typeof opts.tooltip === 'function')? opts.tooltip(this): opts.tooltip,
					element = this;
					$('body').append(structure.replace(/___EXTRA_CSS___/, css).replace(/___CONTENT___/, tooltip));
					$('body > div.tooltip:last').css("display", "none").css("position", "absolute").css("opacity", "0.9").css("padding", "10px").css("top", (e.pageY - opts.xOffset) + "px").css("left", (e.pageX - opts.yOffset) + "px").fadeIn("fast");
				},
				function() {
					$('body > div.tooltip:last').remove();
				}
			).mousemove(
				function(e) {
					$('body > div.tooltip:last').css("top",(e.pageY - opts.xOffset) + "px")
                       .css("left",(e.pageX + opts.yOffset) + "px");
				}
			);
 		});
	};
}(jQuery));