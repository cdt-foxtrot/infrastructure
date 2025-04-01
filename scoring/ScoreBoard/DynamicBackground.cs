using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using System;
using System.Collections.Generic;
using System.Net.Mime;

namespace Scoreboard
{
    /// <summary>
    /// Controls the background of the UI.
    /// </summary>
    public class DynamicBackground
    {

        // Fields:
        private Vector2 m_v2TopBottomOffset;
        private Texture2D m_pBackdrop;
        private Rectangle m_rBackRect;
        private Texture2D m_pEdges;
        private List<Rectangle> m_lEdgeRects;

        // Properties: - NONE -

        // Constructors:
        /// <summary>
        /// Creates a generic background texture using the default background.
        /// </summary>
        /// <param name="a_pGraphics">Graphics device for</param>
        public DynamicBackground(GraphicsDevice a_pGraphics, ContentManager a_pContent)
        {
            m_v2TopBottomOffset = Vector2.Zero;
            m_pBackdrop = a_pContent.Load<Texture2D>("Minecraft_Background");
            m_pEdges = null!;

            m_rBackRect = new Rectangle(0, 0, a_pGraphics.Viewport.Width, a_pGraphics.Viewport.Height);
            m_lEdgeRects = new List<Rectangle>();
        }

        /// <summary>
        /// Constructor containing the offsets for objects from all around.
        /// </summary>
        /// <param name="a_pGraphics">Graphics object used to create the texture.</param>
        /// <param name="a_v2TopBottomOffset">Offset from the top/bottom/left/right.</param>
        public DynamicBackground(GraphicsDevice a_pGraphics, Vector2 a_v2TopBottomOffset)
        {
            m_v2TopBottomOffset = a_v2TopBottomOffset;
            m_pBackdrop = new Texture2D(a_pGraphics, 1, 1);
            m_pBackdrop.SetData<Color>(new Color[1] { new Color(new Vector3(0.77f, 0.77f, 0.77f)) });

            m_pEdges = new Texture2D(a_pGraphics, 1, 1);
            m_pEdges.SetData<Color>(new Color[1] { new Color(new Vector3(0.33f, 0.33f, 0.33f)) });

            m_rBackRect = new Rectangle(
                (int)m_v2TopBottomOffset.X,
                (int)m_v2TopBottomOffset.Y, 
                (int)(a_pGraphics.Viewport.Width - (2 * m_v2TopBottomOffset.X)), 
                (int)(a_pGraphics.Viewport.Height - (2 * m_v2TopBottomOffset.Y)));
            m_lEdgeRects = new List<Rectangle>();

            SetEdgeRectangles();
        }

        // Methods:
        /// <summary>
        /// Clears the list of edge rectangle positions and creates a new set of them.
        /// </summary>
        private void SetEdgeRectangles()
        {
            int dBorderThickness = 4;
            m_lEdgeRects.Clear();

            m_lEdgeRects.Add(new Rectangle(
                (int)m_v2TopBottomOffset.X,
                (int)m_v2TopBottomOffset.Y,
                dBorderThickness,
                m_rBackRect.Height));
            m_lEdgeRects.Add(new Rectangle(
                (int)m_v2TopBottomOffset.X,
                (int)m_v2TopBottomOffset.Y,
                m_rBackRect.Width,
                dBorderThickness));
            m_lEdgeRects.Add(new Rectangle(
                (int)m_v2TopBottomOffset.X + m_rBackRect.Width - dBorderThickness,
                (int)m_v2TopBottomOffset.Y,
                dBorderThickness,
                m_rBackRect.Height));
            m_lEdgeRects.Add(new Rectangle(
                (int)m_v2TopBottomOffset.X,
                (int)m_v2TopBottomOffset.Y + m_rBackRect.Height - dBorderThickness,
                m_rBackRect.Width,
                dBorderThickness));
        }

        /// <summary>
        /// Frame to Frame draw method for the UI.
        /// </summary>
        /// <param name="a_pSpriteBatch">SpriteBatch being used to render the textures.</param>
        public void Draw(SpriteBatch a_pSpriteBatch)
        {
            a_pSpriteBatch.Draw(
                m_pBackdrop,
                m_rBackRect,
                Color.White);

            if (m_pEdges is not null && m_lEdgeRects is not null)
            {
                foreach (Rectangle source in m_lEdgeRects)
                {
                    a_pSpriteBatch.Draw(
                        m_pEdges,
                        source,
                        Color.White);
                }    
            }
        }

        /// <summary>
        /// Called whenever the window resizes to keep the UI in the same place.
        /// </summary>
        /// <param name="a_pGraphics">Graphics object for getting the Viewport.</param>
        public void OnResize(GraphicsDeviceManager a_pGraphics)
        {
            m_rBackRect = new Rectangle(
                (int)m_v2TopBottomOffset.X,
                (int)m_v2TopBottomOffset.Y,
                (int)(a_pGraphics.GraphicsDevice.Viewport.Width - (2 * m_v2TopBottomOffset.X)),
                (int)(a_pGraphics.GraphicsDevice.Viewport.Height - (2 * m_v2TopBottomOffset.Y)));
            SetEdgeRectangles();
        }

    }
}
