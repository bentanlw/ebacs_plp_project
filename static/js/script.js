(function () {
    var Message;
    Message = function (arg) {
        this.text = arg.text, this.message_side = arg.message_side;
        this.draw = function (_this) {
            return function () {
                var $message;
                $message = $($('.message_template').clone().html());
                $message.addClass(_this.message_side).find('.text').html(_this.text);
                if (_this.message_side == 'left') {
                    $message.find('.avatar').text("RB");
                }
                $('.messages').append($message);
                return setTimeout(function () {
                    return $message.addClass('appeared');
                }, 0);
            };
        }(this);
        return this;
    };
    $(function () {
        var getMessageText, message_side, sendMessage;
        message_side = 'left';
        getMessageText = function () {
            var $message_input;
            $message_input = $('.message_input');
            return $message_input.val();
        };

        sendMessage = function (text, speaker) {
            var $messages, message;
            if (text.trim() === '') {
                return;
            }
            $('.message_input').val('');
            $messages = $('.messages');
            if (speaker === 'user') {
              message_side = 'right';
            } else {
              message_side = 'left';
              
            }

            message = new Message({
                text: text,
                message_side: message_side
            });
            message.draw();
            return $messages.animate({ scrollTop: $messages.prop('scrollHeight') }, 300);
        };

        $('.send_message').click(function (e) {
            $.get("/get", {msg: getMessageText()}).done(function(data){
              sendMessage(getMessageText(), 'user');
              sendMessage(data, 'bot');
            });
            return; 
        });

        $('.message_input').keyup(function (e) {
            if (e.which === 13) {
                $.get("/get", {msg: getMessageText()}).done(function(data){
                sendMessage(getMessageText(), 'user');
                sendMessage(data, 'bot');
              });
            };
        });
        setTimeout(function () {
          return sendMessage("Hi! I can help with a recommendation, an enquiry or even reservations!", 'bot');
        }, 500);
        return setTimeout(0);
    });
}.call(this));