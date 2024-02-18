import ROOT

ROOT.TGaxis.SetMaxDigits(3)

#ROOT.gStyle.SetPalette(ROOT.kRainBow)  #Default
#ROOT.gStyle.SetPalette(ROOT.kBird) 
ROOT.gStyle.SetPalette(ROOT.kDarkBodyRadiator) 

icol=0
ROOT.gStyle.SetFrameBorderMode(icol)
ROOT.gStyle.SetFrameFillColor(icol)
ROOT.gStyle.SetCanvasBorderMode(icol)
ROOT.gStyle.SetCanvasColor(icol)
ROOT.gStyle.SetPadBorderMode(icol)
ROOT.gStyle.SetPadColor(icol)
ROOT.gStyle.SetStatColor(icol)

ROOT.gStyle.SetPaperSize(20,26)

ROOT.gStyle.SetPadTopMargin(0.05)
ROOT.gStyle.SetPadRightMargin(0.10)#THIS WAS 0.05 BUT LABELS IN EXPONENTIAL NOTATION CANNOT BE SEEN IN THIS WAY
ROOT.gStyle.SetPadBottomMargin(0.16)
ROOT.gStyle.SetPadLeftMargin(0.16)

ROOT.gStyle.SetTitleXOffset(1.4)
ROOT.gStyle.SetTitleYOffset(1.4)

font=42
tsize=0.05
ROOT.gStyle.SetTextFont(font)

ROOT.gStyle.SetTextSize(tsize)
ROOT.gStyle.SetLabelFont(font,"x")
ROOT.gStyle.SetTitleFont(font,"x")
ROOT.gStyle.SetLabelFont(font,"y")
ROOT.gStyle.SetTitleFont(font,"y")
ROOT.gStyle.SetLabelFont(font,"z")
ROOT.gStyle.SetTitleFont(font,"z")


ROOT.gStyle.SetLabelSize(tsize,"x")
ROOT.gStyle.SetTitleSize(tsize,"x")

ROOT.gStyle.SetLabelSize(tsize,"y")
ROOT.gStyle.SetTitleSize(tsize,"y")

ROOT.gStyle.SetLabelSize(tsize,"z")
ROOT.gStyle.SetTitleSize(tsize,"z")

ROOT.gStyle.SetMarkerStyle(20)
ROOT.gStyle.SetMarkerSize(1.2)
ROOT.gStyle.SetHistLineWidth(2)
ROOT.gStyle.SetLineStyleString(2,"[12 12]")

ROOT.gStyle.SetEndErrorSize(0.)

ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(0)

ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
