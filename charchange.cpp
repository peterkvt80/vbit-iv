#include "charchange.h"

CharChange::CharChange() : next(nullptr), m_OldChar(' '), m_NewChar(' '), m_CursorLoc(wxPoint(0,0))
{
    //ctor
}

CharChange::~CharChange()
{
    //dtor
    if (next!=nullptr)
    {
        std::cout << "TODO: need to destruct any remaining changes in this list" << std::endl;
        delete next;
    }
}

void CharChange::AddChange(wxPoint wxc,char oldchar, char newchar)
{
    m_CursorLoc=wxc;
    m_OldChar=oldchar;
    m_NewChar=newchar;
    std::cout << "AddChange x,y=" <<wxc.x<<","<<wxc.y << "old=>new=" << oldchar <<"=>"<<newchar << std::endl;
}
