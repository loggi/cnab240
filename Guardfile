notification(:libnotify, {
      display_message: true,
        display_title: true,
})


guard :shell do
  watch(/.*\.py/) do |m|
    if system("./run_tests.sh")
       n "All tests ok"
    else
       n "Tests failing"
    end
  end
end
