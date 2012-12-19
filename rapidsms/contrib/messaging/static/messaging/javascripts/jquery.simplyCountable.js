/*
* jQuery Simply Countable plugin
* Provides a character counter for any text input or textarea
* 
* @version  0.4.2
* @homepage http://github.com/aaronrussell/jquery-simply-countable/
* @author   Aaron Russell (http://www.aaronrussell.co.uk)
*
* Copyright (c) 2009-2010 Aaron Russell (aaron@gc4.co.uk)
* Dual licensed under the MIT (http://www.opensource.org/licenses/mit-license.php)
* and GPL (http://www.opensource.org/licenses/gpl-license.php) licenses.
*/

(function($){

  $.fn.simplyCountable = function(options){
    
    options = $.extend({
      counter:            '#counter',
      countType:          'characters',
      wordSeparator:      ' ',
      maxCount:           140,
      strictMax:          false,
      countDirection:     'down',
      safeClass:          'safe',
      overClass:          'over',
      thousandSeparator:  ',',
      onOverCount:        function(){},
      onSafeCount:        function(){},
      onMaxCount:         function(){}
    }, options);
    
    var countable = this;
    var counter = $(options.counter);
    if (!counter.length) { return false; }
    regex = new RegExp('['+options.wordSeparator+']+');
    
    var countCheck = function(){
           
      var count;
      var revCount;
      
      var reverseCount = function(ct){
        return ct - (ct*2) + options.maxCount;
      }
      
      var countInt = function(){
        return (options.countDirection === 'up') ? revCount : count;
      }
      
      var numberFormat = function(ct){
        var prefix = '';
        if (options.thousandSeparator){
          ct = ct.toString();          
          // Handle large negative numbers
          if (ct.match(/^-/)) { 
            ct = ct.substr(1);
            prefix = '-';
          }
          for (var i = ct.length-3; i > 0; i -= 3){
            ct = ct.substr(0,i) + options.thousandSeparator + ct.substr(i);
          }
        }
        return prefix + ct;
      }
      
      /* Calculates count for either words or characters */
      if (options.countType === 'words'){
        count = options.maxCount - $.trim(countable.val()).split(regex).length;
        if (countable.val() === ''){ count += 1; }
      }
      else { count = options.maxCount - countable.val().length; }
      revCount = reverseCount(count);
      
      /* If strictMax set restrict further characters */
      if (options.strictMax && count <= 0){
        var content = countable.val();
        if (count < 0 || content.match(new RegExp('['+options.wordSeparator+']$'))) {
          options.onMaxCount(countInt(), countable, counter);
        }
        if (options.countType === 'words'){
          countable.val(content.split(regex).slice(0, options.maxCount).join(options.wordSeparator));
        }
        else { countable.val(content.substring(0, options.maxCount)); }
        count = 0, revCount = options.maxCount;
      }
      
      counter.text(numberFormat(countInt()));
      
      /* Set CSS class rules and API callbacks */
      if (!counter.hasClass(options.safeClass) && !counter.hasClass(options.overClass)){
        if (count < 0){ counter.addClass(options.overClass); }
        else { counter.addClass(options.safeClass); }
      }
      else if (count < 0 && counter.hasClass(options.safeClass)){
        counter.removeClass(options.safeClass).addClass(options.overClass);
        options.onOverCount(countInt(), countable, counter);
      }
      else if (count >= 0 && counter.hasClass(options.overClass)){
        counter.removeClass(options.overClass).addClass(options.safeClass);
        options.onSafeCount(countInt(), countable, counter);
      }
      
    };
    
    countCheck();
    countable.keyup(countCheck);
    countable.bind('paste', function(){
      // Wait a few miliseconds for the pasting
      setTimeout(countCheck, 5);
    });
    
  };

})(jQuery);