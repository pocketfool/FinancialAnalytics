#!/usr/bin/perl
use strict;
use warnings;

$|++;

## Imports (use [MODULE] qw/[IMPORTLIST]/;) ##
use X11::GUITest qw/
    WaitWindowViewable
    SendKeys
    SetInputFocus
    GetWindowName
    GetInputFocus
/;


#my $OUTPUT_AUTOFLUSH = 1;
my $login_window = 0;
my $upgrade_window = 0;
my $main_window = 0;
my $connect_window = 0;
my $main_title = '.*Interactive Brokers Trader Workstation';
my $connect_title = ".*IB Trader Workstation";
my $login_title = '.*New Login';
my $upgrade_title = '';
my $short_wait = 30;
my $long_wait = 90;


## execution starts
print "gui helper script started\n";

## wait for the login window and submit it
($login_window) = WaitWindowViewable($login_title, undef, $short_wait);
unless ($login_window) {
    print "could not find login window\n";
    exit(1);
} else {
    print "found login window $login_window\n";
    SetInputFocus($login_window);
    unless (SendKeys("{ENT}{ENT}{ENT}{ENT}")) {
        print "unable to complete login window\n";
        exit(1);
    } else {
        print "sent completion keystrokes to login window $login_window\n";
    }
}

## account for the upgrade window that comes up only sometimes
sleep(3);
$upgrade_window = GetInputFocus();
unless (SendKeys("{TAB SPA}")) {
    print "unable to complete the upgrade window\n";
    exit(1);
} else {
    print "sent completion keystrokes to upgrade window $upgrade_window\n";
}


## wait on the main window
($main_window) = WaitWindowViewable($main_title, undef, $long_wait);
unless ($main_window) {
    print "could not find main window\n";
    exit(1);
} else {
    print "found main window $main_window\n";
}

## wait on the connection window
($connect_window) = WaitWindowViewable($connect_title, undef, $long_wait);
unless ($connect_window) {
    print "could not find connection window\n";
    exit(1);
} else {
    SetInputFocus($connect_window);
    unless (SendKeys("{ENT}")) {
        print "could not complete connection window\n";
        exit(1);
    } else {
        print "sent completion keystrokes to connection window $connect_window\n";
    }
}

## fin
print "gui helper script finished\n";

