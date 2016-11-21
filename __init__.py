from pdfminer.pdfparser import PDFParser #pip install --user pdfminer
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.converter import PDFLayoutAnalyzer, PDFConverter
from pdfminer.converter import LTContainer, LTPage, LTText, LTLine, LTRect, LTCurve, LTFigure, LTImage, LTChar, LTTextLine, LTTextBox, LTTextBoxVertical, LTTextGroup
import sys

def PDF_text( pdf_fp, 
              convert_to_lower_case=True,
              line_overlap = 0.5, #layout parameters defaults
              char_margin = 2.0,  #see https://github.com/euske/pdfminer/blob/master/pdfminer/layout.py#L500
              line_margin = 0.5,
              word_margin = 0.1,
              boxes_flow = 0.5,
              detect_vertical = False,
              all_texts = False
              ):
    'scape PDF text, no position available'
    T = []
    parser = PDFParser(pdf_fp)
    document = PDFDocument(parser) #,password)
    laparams = LAParams( line_overlap=line_overlap, char_margin=char_margin, line_margin=line_margin, word_margin=word_margin, boxes_flow=boxes_flow, detect_vertical=detect_vertical, all_texts=all_texts ) # Set layout parameters for analysis.
    assert laparams.char_margin == char_margin
    rsrcmgr = PDFResourceManager()  # Create a PDF resource manager object that stores shared resources.
    device = PDFPageAggregator(rsrcmgr, laparams=laparams) # Create a PDF page aggregator object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.create_pages(document):
        interpreter.process_page(page)
        # receive the LTPage object for the page.
        layout = device.get_result()
        if layout.groups != None:
            for group in layout.groups[0]:
                if hasattr( group, 'get_text'):
                    T.append( group.get_text().lower() if convert_to_lower_case else group.get_text() )
    pdf_fp.seek(0)
    return T


class Check_Containts:
    def __init__(self, text, error_msg ):
        if type(text) == list:
            self.texts = [ t.lower() for t in text ]
        else:
            self.texts = [text.lower()]
        self.error_msg = error_msg 
        self.matches = 0
    def check( self,  text_in_lower_case ):
        for t in self.texts:
            self.matches += text_in_lower_case.count( t )
    def add_to_error_msgs( self, error_msgs):
        if self.matches == 0:
            error_msgs.append( self.error_msg )

def get_words_following_text(main_text, text, count = 1):
    p1 = main_text.find( text )
    if p1 == -1:
        return None
    words = []
    p3 = p1 + len(text)
    for i in range(count):
        p2 = p3
        while main_text[p2] in ' \t':
            p2 += 1
        p3 = p2
        while main_text[p3] not in ' \n':
            p3 += 1
        words.append( main_text[p2:p3] )
    return words

def get_words_before_text(main_text, text, count = 1):
    p1 = main_text.find( text )
    if p1 == -1:
        return None
    words = []
    p3 = p1-1
    for i in range(count):
        p2 = p3
        while main_text[p2] in ' \t':
            p2 -= 1
        p3 = p2
        while main_text[p3] not in ' \n':
            p3 -= 1
        words.append( main_text[p3+1:p2+1] )
    return words


#modified from pdfminer/convertor.py XMLConverter
class TextPosCovertor(PDFConverter):

    def __init__(self, rsrcmgr, recorder , codec='utf-8', pageno=1,
                 laparams=None, imagewriter=None):
        PDFConverter.__init__(self, rsrcmgr, outfp=sys.stderr, codec='utf-8', pageno=1, laparams=None)
        self.recorder =  recorder #custom class which is definied next

    def write_text(self, text):
        pass

    def receive_layout(self, ltpage):
        #def show_group(item):
        #    if isinstance(item, LTTextBox):
        #        self.outfp.write('<textbox id="%d" bbox="%s" />\n' %
        #                         (item.index, bbox2str(item.bbox)))
        #    elif isinstance(item, LTTextGroup):
        #        self.outfp.write('<textgroup bbox="%s">\n' % bbox2str(item.bbox))
        #        for child in item:
        #            show_group(child)
        #        self.outfp.write('</textgroup>\n')
        #    return

        def render(item):
            if isinstance(item, LTPage):
                #self.outfp.write('<page id="%s" bbox="%s" rotate="%d">\n' % (item.pageid, bbox2str(item.bbox), item.rotate))
                self.recorder.set_page( item.pageid )
                for child in item:
                    render(child)
                #if item.groups is not None:
                    #self.outfp.write('<layout>\n')
                #    for group in item.groups:
                #        show_group(group)
                    #self.outfp.write('</layout>\n')
                #self.outfp.write('</page>\n')
            elif isinstance(item, LTLine):
                #print( '<line linewidth="%d" bbox="%s" />' % (item.linewidth, item.bbox))
                self.recorder.record_LTLine( item )
            elif isinstance(item, LTRect):
                #self.outfp.write('<rect linewidth="%d" bbox="%s" />' % (item.linewidth, item.bbox))
                self.recorder.record_LTRect( item )
            elif isinstance(item, LTCurve):
                #self.outfp.write('<curve linewidth="%d" bbox="%s" pts="%s"/>\n' %
                #                 (item.linewidth, bbox2str(item.bbox), item.get_pts()))
                pass
            elif isinstance(item, LTFigure):
                #self.outfp.write('<figure name="%s" bbox="%s">\n' %
                #                 (item.name, bbox2str(item.bbox)))
                for child in item:
                    render(child)
                #self.outfp.write('</figure>\n')
            elif isinstance(item, LTTextLine):
                #self.outfp.write('<textline bbox="%s">\n' % bbox2str(item.bbox))
                for child in item:
                    render(child)
                #self.outfp.write('</textline>\n')
            elif isinstance(item, LTTextBox):
                #wmode = ''
                #if isinstance(item, LTTextBoxVertical):
                #    wmode = ' wmode="vertical"'
                #self.outfp.write('<textbox id="%d" bbox="%s"%s>\n' %
                #                 (item.index, bbox2str(item.bbox), wmode))
                for child in item:
                    render(child)
                #self.outfp.write('</textbox>\n')
            elif isinstance(item, LTChar):
                #self.outfp.write('<text font="%s" bbox="%s" size="%.3f">' %
                #                 (enc(item.fontname), bbox2str(item.bbox), item.size))
                #self.write_text(item.get_text())
                #self.outfp.write('</text>\n')
                self.recorder.record_LTChar( item )
            elif isinstance(item, LTText):
                #self.outfp.write('<text>%s</text>\n' % item.get_text())
                #print('LTText.get_text() %s' % item.get_text() )
                raise NotImplementedError, item
            elif isinstance(item, LTImage):
                pass
            else:
                raise NotImplementedError, item
            return
        render(ltpage)
        return

    def close(self):
        pass


class PDF_text_get_Error(Exception):
    pass

class PDF_text_with_locations:
    def __init__( self, pdf_fp, 
                  convert_to_lower_case=True,
                  char_margin = 0.2,
                  line_margin = 0.1,
                  space_margin = 1.0,  
                  ignore_fontname = True,
                  record_lines = False,
                  record_rects = False
                  ):
        self.text_groups = {}
        self.char_margin = char_margin
        self.space_margin = space_margin 
        self.line_margin = line_margin 
        self.ignore_fontname = ignore_fontname
        self.record_lines = record_lines
        if record_lines:
            self.lines = {}
        self.record_rects = record_rects
        if record_rects:
            self.rects = {}
        rsrcmgr = PDFResourceManager()
        device = TextPosCovertor(rsrcmgr, self)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.get_pages( pdf_fp, check_extractable=False ):
            interpreter.process_page(page)
        pdf_fp.seek(0)

    def set_page( self, pageid ):
        if not self.text_groups.has_key( pageid ):
            self.text_groups[pageid] = []
        self.current_page = pageid

    def record_LTChar( self, item ):
        #print('LTChar bbox="%s" size="%.3f" %s' % ( item.bbox, item.size, item.get_text() ) )
        
        #print(  item.get_text(), item.bbox )
        if len( self.text_groups[self.current_page] ) == 0 or not self.text_groups[self.current_page][-1].absorb( item, self.char_margin, self.space_margin, self.line_margin, self. ignore_fontname):
            #if len( self.text_groups[self.current_page] ) > 0:
            #    print(  self.text_groups[self.current_page][-1].__dict__)
            #    print( item.__dict__ )
            #    exit()
            self.text_groups[self.current_page].append( PDF_Text_Entry(item, self.current_page, self) )
        #if len( self.text_groups[self.current_page] ) == 10:
        #    exit()

    def findText_above( self, textEnt, tol = 0.5):
        for t in self.text_groups[ textEnt.page_no]:
            if t.bbox[1] < textEnt.bbox[3] and abs( textEnt.bbox[3] - t.bbox[1] ) < textEnt.size * tol and abs( textEnt.bbox[0] - t.bbox[0] ) < textEnt.size * tol and t != textEnt:
                return t
    def findText_below( self, t_ref, tol = 0.5):
        for t in self.text_groups[ t_ref.page_no ]:
            if t_ref.bbox[3] > t.bbox[3] and abs(t_ref.bbox[1] - t.bbox[3]) < t_ref.size * tol and abs( t_ref.bbox[0] - t.bbox[0] ) < t_ref.size * tol and t != t_ref:
                return t

    def findText_same_y( self, t_ref, tol = 0.5):
        return sorted([ t for t in self.text_groups[ t_ref.page_no ]
                 if abs( t_ref.bbox[1] - t.bbox[1] ) < t_ref.size * tol
                 ], key=lambda i: i.bbox[0])

    def findText_right_of( self, t_ref, tol = 0.5):
        T = self.findText_same_y( t_ref, tol )
        return [ t for t in T if t.bbox[0] > t_ref.bbox[0] ][0]

    def filter( self, page=None, text=None, text__startswith=None, text__endswith=None, text__contains=None ):
        if text == None and text__startswith==None and text__endswith==None and text__contains==None:
            raise ValueError, "No searching criterea specified"
        if not page:
            page = self.current_page
        return [ t for t in self.text_groups[page] 
                 if ( text == None or t.text == text) and \
                     ( text__startswith==None or t.text.startswith(text__startswith) ) and \
                     ( text__endswith==None or t.text.endswith(text__endswith) ) and \
                     ( text__contains==None or text__contains in t.text )
                 ]

    def get( self, *args, **kwargs):
        R = self.filter( *args, **kwargs )
        if len(R) == 0:
            raise PDF_text_get_Error, "no matches for %s (%s)" % ( str(args), str(kwargs))
        if len(R) > 1:
            raise PDF_text_get_Error, "multiple matches returned for %s (%s)" % ( str(args), str(kwargs) )
        return R[0]

    def record_LTRect( self, item ):
        if not self.record_rects:
            return 
        if not self.rects.has_key( self.current_page ):
            self.rects[self.current_page] = []
        item.area = item.width * item.height
        self.rects[self.current_page].append(item)
        #print( item )
        #item.__dict__ {'linewidth': 0, 'height': 1.4400000000000546, 'width': 1.4399999999999977, 'bbox': (30.96, 816.6, 32.4, 818.0400000000001), 'y1': 818.0400000000001, 'y0': 816.6, 'x0': 30.96, 'x1': 32.4, 'pts': [(30.96, 816.6), (32.4, 816.6), (32.4, 818.0400000000001), (30.96, 818.0400000000001)]}

    def record_LTLine( self, item ):
        if not self.record_lines:
            return 
        raise NotImplemented

    def to_svg( self, path ):
        assert len( self.text_groups) == 1 #1 page
        width = max( t.bbox[2] for t in self.text_groups[self.current_page] ) + 50
        height = max( t.bbox[3] for t in self.text_groups[self.current_page] ) + 50
        f = open( path, 'w')
        f.write( '''<svg width="%f" height="%f" >
<rect width="%f" height="%f" style="fill:white" />
 \n  %s \n</svg>''' % ( width, height, width, height, '\n  '.join( t.svg(height) for t in self.text_groups[self.current_page]) ) )
        f.close()

def bbox_add( bb1, bb2):
    return ( 
        min( bb1[0], bb2[0] ),
        min( bb1[1], bb2[1] ),
        max( bb1[2], bb2[2] ),
        max( bb1[3], bb2[3] ),
        )

class PDF_Text_Entry:
    def __init__( self, ltChar, page_no, PDF_text_with_locations_instance):
        self.PDF_text_with_locations_instance = PDF_text_with_locations_instance
        self.font = ltChar.fontname
        self.size = ltChar.size
        self.bbox = ltChar.bbox
        self.text = ltChar.get_text()
        self.page_no = page_no
        #print( ltChar.__dict__ )
        #exit()
    def absorb( self, ltChar, char_margin, space_margin, line_margin, ignore_fontname ):
        if abs(self.size - ltChar.size) > 0.01 or ( not ignore_fontname and self.font != ltChar.fontname):
            return False 
        #print( abs(self.bbox[1] - ltChar.bbox[1] ) , self.size * line_margin )
        if abs(self.bbox[1] - ltChar.bbox[1] ) < self.size * line_margin:
            #print(abs(self.bbox[2] - ltChar.bbox[0]), self.size * char_margin)
            if abs(self.bbox[2] - ltChar.bbox[0]) < self.size * char_margin:
                self.text += ltChar.get_text()
                self.bbox = bbox_add( self.bbox, ltChar.bbox )
                return True
            elif abs(self.bbox[2] - ltChar.bbox[0]) < self.size * (char_margin + space_margin):
                self.text += ' ' + ltChar.get_text()
                self.bbox = bbox_add( self.bbox, ltChar.bbox )
                return True
        return False

    def textblock_below( self, tol = 0.5):
        return self.PDF_text_with_locations_instance.findText_below( self, tol )

    def textblock_above( self, tol = 0.5):
        return self.PDF_text_with_locations_instance.findText_above( self, tol )
    
    def textblocks_same_y( self, tol = 0.5):
        return self.PDF_text_with_locations_instance.findText_same_y( self, tol)

    def textblock_right(self, tol = 0.5):
        return self.PDF_text_with_locations_instance.findText_right_of( self, tol )

    def svg( self, page_height ):
        return '<text x="%f" y="%f" size="%f">%s</text>' % ( self.bbox[0], page_height-self.bbox[1], self.size, self.text.encode('utf8') )

    def __lt__( self, b,  tol = 0.1 ):
        "x0 and y0 in page bottom left"
        if self.page_no != b.page_no:
            return  self.page_no < b.page_no
        if abs( self.bbox[1] - b.bbox[1]) > tol:
            return self.bbox[1] > b.bbox[1]
        return self.bbox[0] < b.bbox[0]

    def __repr__( self ):
        return '<PDF_Text_Entry "%s" at %3.3f %3.3f (%s %2.1f)>' % (self.text.encode('utf8'), self.bbox[0], self.bbox[1], self.font, self.size )




def parse_rect_table( pdf, page_no, x, y, table_spans_pages_with = True, tol=2, log=lambda txt:None ):
    assert isinstance( pdf, PDF_text_with_locations )
    assert pdf.record_rects
    if not table_spans_pages_with:
        raise NotImplemented
    v_lines = []
    h_lines = []
    h_line_start = None
    for r in pdf.rects[page_no]:
        #print r.__dict__
        #print( 'rect: width %3.1f, height %3.1f, area %2.1f' % (r.width, r.height, r.area ))
        if r.width > 6 * r.height:
            assert r.x0 < r.x1
            assert r.y0 < r.y1
            h_lines.append(r)
            #print( r.x0 < x, x < r.x1, r.y0 > y )
            if r.x0 < x and x < r.x1 and r.y0 > y:
                if h_line_start == None or abs(r.y0 - y) < abs(h_line_start.y0 - y):
                    h_line_start = r
        elif r.height > 6 * r.width:
            assert r.x0 < r.x1
            assert r.y0 < r.y1
            v_lines.append(r)
    #print( h_line_start )
    HL = [ r for r in h_lines if r.y0 == h_line_start.y0 ] 
    x_min = min( r.x0 for r in HL )
    x_max = max( r.x1 for r in HL )
    #print( len(HL), x_min, x_max )
    M = [ r for r in v_lines if abs(r.x0 - x_min) < tol and abs( r.y0 -  h_line_start.y0 ) < tol ]
    assert len(M) == 1, "len(M) != 1, len(M) = %i" % len(M)
    v_line_start = M[0]
    #print( v_line_start )
    VL_candidates = [ r for r in v_lines if abs(r.x0 - x_min) < tol ]
    #print( VL_candidates )
    VL = [ v_line_start ]
    def line_walk( add, append  ):
        found = False
        for r in VL_candidates:
            if add(r):
                found = True
                if append:
                    VL.append(r)
                else:
                    VL.insert(0,r)
                break
        if found:
            line_walk( add, append  )
    line_walk( lambda r: abs(r.y1 - VL[0].y0) < tol, append=False )
    line_walk( lambda r: abs(r.y0 - VL[-1].y1) < tol, append=True )
    #print( len(VL) )

    table_X = sorted([r.x0 for r in HL]) + [max(r.x1 for r in HL)]
    table_Y = sorted([r.y0 for r in VL]) + [max(r.y1 for r in VL)]
    log('table_X: %s' % ', '.join( '%i'%v for v in table_X) )
    log('table_Y: %s' % ', '.join( '%i'%v for v in table_Y))
    
    n_col = len( table_X ) - 1
    n_row = len( table_Y ) - 1
    T = [ [ [] for col in range( n_col ) ] for row in range(n_row) ]
    for t in pdf.text_groups[page_no]:
        col = sum( t.bbox[0] > c_x for c_x in table_X ) -1
        row = sum( t.bbox[1] > r_y for r_y in table_Y ) -1
        if -1 < col and col < n_col and -1 < row and row < n_row :
            T[row][col].append( t )
    T.reverse() #y flip
    log('Result:')
    table_contents = []
    for row in range(n_row):
        table_contents.append([])
        for col in range(n_col):
            text = ' '.join( t.text.strip() for t in sorted( T[row][col] ) )
            table_contents[-1].append(text)
        log( table_contents[-1] )
    return table_contents
    
