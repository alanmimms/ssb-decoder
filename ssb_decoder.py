#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: SSB decoder
# Author: alan
# GNU Radio version: 3.10.9.2

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSlot
from gnuradio import audio
from gnuradio import blocks
import math
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import sip



class ssb_decoder(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "SSB decoder", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("SSB decoder")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "ssb_decoder")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 300000
        self.audio_rate = audio_rate = 48000
        self.volume = volume = 6
        self.tune = tune = -40000
        self.sideband_filter = sideband_filter = firdes.complex_band_pass(1.0, audio_rate, 300, 3500, 200, window.WIN_HAMMING, 6.76)
        self.sideband = sideband = 1
        self.rf_gain = rf_gain = 10
        self.decim_samp_rate = decim_samp_rate = samp_rate/5

        ##################################################
        # Blocks
        ##################################################

        self._volume_range = qtgui.Range(0, 10, 0.1, 6, 200)
        self._volume_win = qtgui.RangeWidget(self._volume_range, self.set_volume, "Volume", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._volume_win)
        self._tune_range = qtgui.Range(-250000, 250000, 100, -40000, 200)
        self._tune_win = qtgui.RangeWidget(self._tune_range, self.set_tune, "Tune", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._tune_win)
        # Create the options list
        self._sideband_options = [0, 1]
        # Create the labels list
        self._sideband_labels = ['USB', 'LSB']
        # Create the combo box
        self._sideband_tool_bar = Qt.QToolBar(self)
        self._sideband_tool_bar.addWidget(Qt.QLabel("Sideband" + ": "))
        self._sideband_combo_box = Qt.QComboBox()
        self._sideband_tool_bar.addWidget(self._sideband_combo_box)
        for _label in self._sideband_labels: self._sideband_combo_box.addItem(_label)
        self._sideband_callback = lambda i: Qt.QMetaObject.invokeMethod(self._sideband_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._sideband_options.index(i)))
        self._sideband_callback(self.sideband)
        self._sideband_combo_box.currentIndexChanged.connect(
            lambda i: self.set_sideband(self._sideband_options[i]))
        # Create the radio buttons
        self.top_layout.addWidget(self._sideband_tool_bar)
        self._rf_gain_range = qtgui.Range(0, 100, 0.1, 10, 200)
        self._rf_gain_win = qtgui.RangeWidget(self._rf_gain_range, self.set_rf_gain, "RF Gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._rf_gain_win)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=audio_rate,
                decimation=samp_rate,
                taps=[],
                fractional_bw=0)
        self.qtgui_sink_x_1_0 = qtgui.sink_c(
            2048, #fftsize
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "baseband", #name
            False, #plotfreq
            True, #plotwaterfall
            False, #plottime
            False, #plotconst
            None # parent
        )
        self.qtgui_sink_x_1_0.set_update_time(1.0/50)
        self._qtgui_sink_x_1_0_win = sip.wrapinstance(self.qtgui_sink_x_1_0.qwidget(), Qt.QWidget)

        self.qtgui_sink_x_1_0.enable_rf_freq(False)

        self.top_layout.addWidget(self._qtgui_sink_x_1_0_win)
        self.qtgui_sink_x_1 = qtgui.sink_c(
            2048, #fftsize
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "RF", #name
            True, #plotfreq
            True, #plotwaterfall
            False, #plottime
            False, #plotconst
            None # parent
        )
        self.qtgui_sink_x_1.set_update_time(1.0/50)
        self._qtgui_sink_x_1_win = sip.wrapinstance(self.qtgui_sink_x_1.qwidget(), Qt.QWidget)

        self.qtgui_sink_x_1.enable_rf_freq(False)

        self.top_layout.addWidget(self._qtgui_sink_x_1_win)
        self.qtgui_sink_x_0 = qtgui.sink_c(
            1024, #fftsize
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            audio_rate, #bw
            "", #name
            True, #plotfreq
            True, #plotwaterfall
            False, #plottime
            False, #plotconst
            None # parent
        )
        self.qtgui_sink_x_0.set_update_time(1.0/10)
        self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.qwidget(), Qt.QWidget)

        self.qtgui_sink_x_0.enable_rf_freq(False)

        self.top_layout.addWidget(self._qtgui_sink_x_0_win)
        self.filter_fft_low_pass_filter_0 = filter.fft_filter_ccc(1, firdes.low_pass(rf_gain, audio_rate, 3500, 50, window.WIN_HAMMING, 6.76), 1)
        self.blocks_wavfile_source_0 = blocks.wavfile_source('/home/alan/ham/sample-iq-data/40m/SDRuno_20200912_004330Z_7150kHz.wav', True)
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_swapiq_0 = blocks.swap_iq(1, gr.sizeof_gr_complex)
        self.blocks_selector_0 = blocks.selector(gr.sizeof_gr_complex*1,sideband,0)
        self.blocks_selector_0.set_enabled(True)
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_ff(volume)
        self.blocks_freqshift_cc_0 = blocks.rotator_cc(2.0*math.pi*tune/samp_rate)
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_complex_to_real_0 = blocks.complex_to_real(1)
        self.audio_sink_0 = audio.sink(audio_rate, '', True)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_complex_to_real_0, 0), (self.blocks_multiply_const_vxx_1, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.blocks_freqshift_cc_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.audio_sink_0, 0))
        self.connect((self.blocks_selector_0, 0), (self.blocks_complex_to_real_0, 0))
        self.connect((self.blocks_selector_0, 0), (self.qtgui_sink_x_0, 0))
        self.connect((self.blocks_swapiq_0, 0), (self.blocks_selector_0, 1))
        self.connect((self.blocks_throttle2_0, 0), (self.blocks_freqshift_cc_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.qtgui_sink_x_1, 0))
        self.connect((self.blocks_wavfile_source_0, 1), (self.blocks_float_to_complex_0, 1))
        self.connect((self.blocks_wavfile_source_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.filter_fft_low_pass_filter_0, 0), (self.blocks_selector_0, 0))
        self.connect((self.filter_fft_low_pass_filter_0, 0), (self.blocks_swapiq_0, 0))
        self.connect((self.filter_fft_low_pass_filter_0, 0), (self.qtgui_sink_x_1_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.filter_fft_low_pass_filter_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "ssb_decoder")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_decim_samp_rate(self.samp_rate/5)
        self.blocks_freqshift_cc_0.set_phase_inc(2.0*math.pi*self.tune/self.samp_rate)
        self.blocks_throttle2_0.set_sample_rate(self.samp_rate)
        self.qtgui_sink_x_1.set_frequency_range(0, self.samp_rate)
        self.qtgui_sink_x_1_0.set_frequency_range(0, self.samp_rate)

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate
        self.set_sideband_filter(firdes.complex_band_pass(1.0, self.audio_rate, 300, 3500, 200, window.WIN_HAMMING, 6.76))
        self.filter_fft_low_pass_filter_0.set_taps(firdes.low_pass(self.rf_gain, self.audio_rate, 3500, 50, window.WIN_HAMMING, 6.76))
        self.qtgui_sink_x_0.set_frequency_range(0, self.audio_rate)

    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume
        self.blocks_multiply_const_vxx_1.set_k(self.volume)

    def get_tune(self):
        return self.tune

    def set_tune(self, tune):
        self.tune = tune
        self.blocks_freqshift_cc_0.set_phase_inc(2.0*math.pi*self.tune/self.samp_rate)

    def get_sideband_filter(self):
        return self.sideband_filter

    def set_sideband_filter(self, sideband_filter):
        self.sideband_filter = sideband_filter

    def get_sideband(self):
        return self.sideband

    def set_sideband(self, sideband):
        self.sideband = sideband
        self._sideband_callback(self.sideband)
        self.blocks_selector_0.set_input_index(self.sideband)

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        self.filter_fft_low_pass_filter_0.set_taps(firdes.low_pass(self.rf_gain, self.audio_rate, 3500, 50, window.WIN_HAMMING, 6.76))

    def get_decim_samp_rate(self):
        return self.decim_samp_rate

    def set_decim_samp_rate(self, decim_samp_rate):
        self.decim_samp_rate = decim_samp_rate




def main(top_block_cls=ssb_decoder, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
