odoo.define('2m_production.count_down', function (require) {
  "use strict";
  
  var fields = require('web.basic_fields');
  var fieldUtils = require('web.field_utils');
  var field_registry = require('web.field_registry');


  
  var CountDownTimer = fields.FieldFloatTime.extend({
  
      init: function () {
          this._super.apply(this, arguments);
          this.remaining_time = this.record.data.remaining_time;
      },
      _renderReadonly: function () {
        if (this.record.data.remaining_time) {
            this._startTimeCounter();
        } else {
            this._super.apply(this, arguments);
        }
    },
    _startTimeCounter: function(){
        var self = this;
        clearTimeout(this.timer);
        this.timer = setInterval(function() {
          if (self.remaining_time > 0) {
              self.remaining_time -= 1;
              self.$el.html($('<span>' +self.secondsToDhms(self.remaining_time) + '</span>'));
            }
            else {
              self.$el.html($('<span>' +self.secondsToDhms(0.0) + '</span>'));
            }
            }, 1000);
    },
    secondsToDhms: function(seconds) {
      seconds = Number(seconds);
      const d = Math.floor(seconds / (3600 * 24));
      const h = Math.floor((seconds % (3600 * 24)) / 3600);
      const m = Math.floor((seconds % 3600) / 60);
      const s = Math.floor(seconds % 60);

      var dDisplay = d >= 0 ? "<span style='font-family: Consolas;font-size:24px;letter-spacing: .25em'>"+("0" + d).slice(-2)+"</span>":"";
      var hDisplay = h >= 0 ? "<span style='font-family: Consolas;font-size:24px;letter-spacing: .25em'>"+("0" + h).slice(-2)+"</span>":"";
      var mDisplay = m >= 0 ? "<span style='font-family: Consolas;font-size:24px;letter-spacing: .25em'>"+("0" + m).slice(-2)+"</span>":"";
      var sDisplay = s >= 0 ? "<span style='font-family: Consolas;font-size:24px;letter-spacing: .25em'>"+("0" + s).slice(-2)+"</span>":"";
      return dDisplay +"<span style='font-family: Consolas;font-size:18px;letter-spacing: .50em'>:</span>"+hDisplay+"<span style='font-family: Consolas;font-size:18px;letter-spacing: .50em'>:</span>"+ mDisplay +"<span style='font-family: Consolas;font-size:18px;letter-spacing: .50em'>:</span>"+ sDisplay;
      },
    
  });
  
  field_registry
      .add('count_down_widget', CountDownTimer)
  
  fieldUtils.format.count_down_widget = fieldUtils.format.float_time;
  });
  