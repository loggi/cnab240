notification(:libnotify, {
      display_message: true,
        display_title: true,
})


guard :shell do
  watch(/.*/) do |m|
    if system("./run_tests.sh")
       n "All tests ok"
    else
       n "Tests failing"
    end
    if system("xenon -bB -mA -aA")
       n "Complexity is good"
    else
       n "Bad codebase"
    end
  end
end
