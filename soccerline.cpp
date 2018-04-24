/**
 * Line detection code for soccer fields
 * Company: SURE Innovations
 * Date: 22-11-2017
 * Contributors: 
 *      - Louis van Harten
 *      - Jeroen van Oorschot
*/

#include "opencv2/imgcodecs.hpp"
#include "opencv2/highgui/highgui.hpp"
#include "opencv2/imgproc/imgproc.hpp"

#include <iostream>
#include <ctime>
#include <iostream>
#include <raspicam/raspicam_cv.h>
#include <math.h>

#define SHOWIMS 0    //Show processed image viewer
#define SHOWIMSSRC 0 //Show source image viewer
#define HUESPLIT 0   //Use both hue and value calculation. Zero for only val, which works best.
#define PRINT 0      //print debugdata to console
#define PLOTALL 0    //plot all detected lines
#define SAVEVID 0   // save output video as out.x264
#define IMAGE_HEIGHT 480
#define IMAGE_WIDTH 640
#define CROP_DIST_FROM_TOP 0 //amount of pixels to crop from top
#define CROP_RES_HEIGHT (IMAGE_HEIGHT - CROP_DIST_FROM_TOP)
#define ALLOWED_RANGE 0.2 //allowed fraction of pi deviation from 0
#define NONZERO_FACTOR 15

using namespace cv;
using namespace std;

int use_video=0;
Mat src;

// Input: black/white mask of (mostly) valid line pixels
void getLinesFromMask(Mat range_dst, Mat crange_dst, int id) {
    vector<Vec2f> lines;
#if PRINT
    cout<<"		Getting Houghlines..."<<endl;
#endif
    HoughLines(range_dst, lines, 1, CV_PI/180, 40, 0, 0 );
#if PRINT
    cout << "nlines: " << lines.size() <<endl;
    cout<<"		Plotting Houghlines..."<<endl;
#endif
    if(lines.size()) {
#if SHOWIMS
        Point pt1, pt2;
#endif
        double a, b, x0, y0, x_o_avg=0, theta_avg=0;
        int tot_points=0;
        for( size_t i = 0; i < lines.size() && i<100; i++ )
        {
            float theta;
            theta = lines[i][1];
            if(theta < 3.141 * ALLOWED_RANGE || theta > 3.141 *(1-ALLOWED_RANGE)) { //ignore non-steep angles
                tot_points++;
                a = cos(theta), b = sin(theta);
                x0 = a*lines[i][0], y0 = b*lines[i][0];
                if(signbit(lines[i][0])){
                    theta = theta-CV_PI;
                }
                x_o_avg += x0 - (IMAGE_HEIGHT-y0)*tan(theta);  //x coord of origin (bottom)
                theta_avg += theta; 
#if PLOTALL //plot all
                pt1.x = cvRound(x0 + 1000*(-b));
                pt1.y = cvRound(y0 + 1000*(a));
                pt2.x = cvRound(x0 - 1000*(-b));
                pt2.y = cvRound(y0 - 1000*(a));
                line( crange_dst, pt1, pt2, Scalar(255,0,255), 3, CV_AA);
#endif
            }
        }

        if(theta_avg || x_o_avg) {
            theta_avg /= tot_points;
            x_o_avg /= tot_points;
            printf("[%i, %.3f, %.3f, %i]\n", id, 2*x_o_avg/IMAGE_WIDTH-1, theta_avg, tot_points);
            fflush(stdout);
#if SHOWIMS  //plot averaged line
            pt1 = Point(int(x_o_avg+tan(theta_avg)*IMAGE_HEIGHT), 0);
            pt2 = Point(int(x_o_avg), IMAGE_HEIGHT);
            line(src, pt1, pt2, Scalar(255,255,0), 3, CV_AA);
            circle(src,pt1, 10, Scalar(255,0,0), 3); // test point to check theta_str
            circle(src,pt2, 10, Scalar(0,255,0), 3); // x coord at bottom image
#endif
        } else {
#if SHOWIMS
            putText(src, "No probable line found", Point(10,30), FONT_HERSHEY_SIMPLEX, 1, Scalar(0,0,255), 2);
#endif
            printf("[%i, \"no probable line\"]\n", id);
            fflush(stdout);
        }

        //printf("\x1b[1;36mStrongest line -- Rho: %.3f, Theta: %.3f\x1b[0m\n", rho_str, theta_str);  //debug info print
        //printf("finish: [%i, %.3f, %.3f]\n", id, rho_str, theta_str); //output as rho theta
    } else {
        //printf("\x1b[1;41mNo lines above threshold!\x1b[0m\n");
        printf("[%i, \"no lines above thresh\"]\n", id);
        fflush(stdout);
    }

#if SHOWIMS
    waitKey(1);
    if(id) {
        imshow("detected lines (hue)", crange_dst);
    } else {
        imshow("detected lines (val)", crange_dst);
        imshow("src", src);
    }
#endif
#if OUTVID
    out_vid << src;
#endif
}

int main(int argc, char** argv)
{
    Mat dst, range_dst_hue, range_dst, crange_dst_hue, crange_dst, src_hsv;
    raspicam::RaspiCam_Cv Camera;
#if SAVEVID
    CvVideoWriter *out_vid;
#endif
    cv::CommandLineParser parser(argc, argv,
        "{help h||}{@video||}"
    );

    
    string filename = parser.get<string>("@video");
    VideoCapture vid(filename);
    if (filename.empty())
    {
        use_video=1;
        //set camera params
        Camera.set(CV_CAP_PROP_FORMAT, CV_8UC3 );
        Camera.set(CV_CAP_PROP_FRAME_WIDTH, 640);
        Camera.set(CV_CAP_PROP_FRAME_HEIGHT, IMAGE_HEIGHT);
#if PRINT
        cout<<"		Opening Camera..."<<endl;
#endif
        if (!Camera.open()) {
            cerr<<"Error opening the camera"<<endl;
            return -1;
        }
    } else {
        if(!vid.isOpened())
        {
            cout << "can not open " << filename << endl;
            return -1;
        }
    }

    do {

        if(use_video) {
#if PRINT
            cout<<"		Grabbing frame..."<<endl;
#endif
            Camera.grab();
            Camera.retrieve (src);
        } else {
            vid >> src;
        }
#if SAVEVID
        out_vid = VideoWriter::VideoWriter("output.x264", VideoWriter::fourcc('X','2','6','4'), 20.0, Size(640, 480), true);
#endif
        Mat cropsrc;
        Rect botcroprect(0,CROP_DIST_FROM_TOP, src.cols, CROP_RES_HEIGHT);
        src(botcroprect).copyTo(cropsrc);

#if HUESPLIT 
        //the "second opinion". Should work better with a non-IR camera
        //may need some value tweaking with new camera
        cvtColor(cropsrc, src_hsv, COLOR_BGR2HSV);
        inRange(src_hsv, Scalar(0,0,0), Scalar(255,70,255), range_dst_hue);
        erode(range_dst_hue, range_dst_hue, getStructuringElement(MORPH_RECT, Size(2,2)), Point(-1,-1),1);
#if PRINT        
        printf("nonzero: %d, lim: %d\n", countNonZero(range_dst_hue), IMAGE_WIDTH*CROP_RES_HEIGHT/NONZERO_FACTOR);
#endif
        for(int i=0;  i<65; i+=3){
            if(countNonZero(range_dst_hue) < IMAGE_WIDTH*CROP_RES_HEIGHT/NONZERO_FACTOR)
                break;
            inRange(src_hsv, Scalar(0,0,0), Scalar(255,50-i,255), range_dst_hue);
            erode(range_dst_hue, range_dst_hue, getStructuringElement(MORPH_RECT, Size(2,2)), Point(-1,-1),1);
#if PRINT      
            printf("nonzero: %d, lim: %d\n", countNonZero(range_dst_hue), IMAGE_WIDTH*CROP_RES_HEIGHT/NONZERO_FACTOR);
#endif
        };
        cvtColor(range_dst_hue, crange_dst_hue, COLOR_GRAY2BGR);
        Canny(crange_dst_hue,range_dst_hue,50,200,5);
        dilate(range_dst_hue, range_dst_hue, getStructuringElement(MORPH_RECT, Size(2,2)), Point(-1,-1),1);
        cvtColor(range_dst_hue, crange_dst_hue, COLOR_GRAY2BGR);

        getLinesFromMask(range_dst_hue, crange_dst_hue, 1);
        
#endif
        Mat cropsrc_lab;
        cvtColor(cropsrc, cropsrc_lab, CV_BGR2Lab);
        vector<cv::Mat> lab_planes(3);
        split(cropsrc_lab, lab_planes);

        Ptr<CLAHE> clahe = createCLAHE();
        clahe->setClipLimit(4);
        Mat labdst;
        clahe->apply(lab_planes[0], labdst);
        labdst.copyTo(lab_planes[0]);
        merge(lab_planes, cropsrc_lab);
        Mat image_clahe;
        cvtColor(cropsrc_lab, image_clahe, CV_Lab2BGR);

#if SHOWIMSSRC
        imshow("claheres", image_clahe);
        imshow("cropsrc", cropsrc);
#endif

        Mat nsrc_hsv;
        cvtColor(image_clahe, nsrc_hsv, COLOR_BGR2HSV);
        inRange(nsrc_hsv, cv::Scalar(0,0,192), cv::Scalar(255,255,255), range_dst);
        erode(range_dst, range_dst, getStructuringElement(MORPH_RECT, Size(2,2)), Point(-1,-1),2);
        dilate(range_dst, range_dst, getStructuringElement(MORPH_RECT, Size(3,3)), Point(-1,-1),2);

        cvtColor(range_dst, crange_dst, COLOR_GRAY2BGR);

        getLinesFromMask(range_dst, crange_dst, 0);

    } while(1);
    Camera.release();
#if SAVEVID
//    out_vid.release();
#endif
    while((waitKey() & 0xEFFFFF) != 27);
    waitKey();

    return 0;
}
