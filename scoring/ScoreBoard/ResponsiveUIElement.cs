using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using System;

namespace Scoreboard
{
    /// <summary>
    /// Container class for the Texture2D object but also contains the logic for dynamic resizing.
    /// </summary>
    public class ResponsiveUIElement
    {

        // Fields:
        private Texture2D m_pTexture;
        private Rectangle m_rScreenPosition;

        // Properties:
        /// <summary>
        /// Returns the upper left position of the Texture.
        /// </summary>
        public Vector2 Position
        {
            get { return m_rScreenPosition.Location.ToVector2(); }
        }

        /// <summary>
        /// Gets/Sets the active texture of the texture.
        /// </summary>
        public Texture2D Texture
        {
            get { return m_pTexture; }
            set { m_pTexture = value; }
        }

        // Constructors:
        /// <summary>
        /// Fundamentally a default constructor only taking in the Texture of the Responsive texture.
        /// </summary>
        /// <param name="a_pTexture">Texture being used by this class.</param>
        public ResponsiveUIElement(Texture2D a_pTexture)
        {
            m_pTexture = a_pTexture;
            m_rScreenPosition = new Rectangle(0, 0, 100, 100);
        }

        /// <summary>
        /// Parameterized constructor taking in the texture and the screen position
        /// </summary>
        /// <param name="a_pTexture">Texture for the window.</param>
        /// <param name="a_v2Position">Position on the texture in the window.</param>
        public ResponsiveUIElement(Texture2D a_pTexture, Vector2 a_v2Position)
        {
            m_pTexture = a_pTexture;
            m_rScreenPosition = new Rectangle((int)a_v2Position.X, (int)a_v2Position.Y, 50, 50);
        }

        // Methods:
        /// <summary>
        /// Draws the texture in the specified rectangle area.
        /// </summary>
        /// <param name="a_pSpriteBatch">SpriteBatch used to render the texture.</param>
        public void Draw(SpriteBatch a_pSpriteBatch)
        {
            a_pSpriteBatch.Draw(
                m_pTexture,
                m_rScreenPosition,
                Color.White);
        }

        /// <summary>
        /// Draws the texture in the specified rectangle area. Allows for color tinting.
        /// </summary>
        /// <param name="a_pSpriteBatch">SpriteBatch used to render the texture.</param>
        /// <param name="a_cTint">Tint of the texture being drawn.</param>
        public void Draw(SpriteBatch a_pSpriteBatch, Color a_cTint)
        {
            a_pSpriteBatch.Draw(
                m_pTexture,
                m_rScreenPosition,
                a_cTint);
        }

        /// <summary>
        /// Resizes the image to fit the size of the window.
        /// </summary>
        /// <param name="a_pGraphics">Graphics device manager used to get the new viewport.</param>
        public void OnResize(GraphicsDeviceManager a_pGraphics)
        {
            m_rScreenPosition.Width = a_pGraphics.GraphicsDevice.Viewport.Width;
            m_rScreenPosition.Height = a_pGraphics.GraphicsDevice.Viewport.Height;
        }

        /// <summary>
        /// Resizes the image to fit the size of the window.
        /// </summary>
        /// <param name="a_pGraphics">Graphics device manager used to get the new viewport.</param>
        /// <param name="a_v2PercentAcross">Places the top left corner point of the texture a 
        ///                                 specified percentage of the actual new viewport.</param>
        public void OnResize(GraphicsDeviceManager a_pGraphics, Vector2 a_v2PercentAcross)
        {
            m_rScreenPosition.Width = (int)(a_pGraphics.GraphicsDevice.Viewport.Width * a_v2PercentAcross.X);
            m_rScreenPosition.Height = (int)(a_pGraphics.GraphicsDevice.Viewport.Height * a_v2PercentAcross.Y);
        }

        /// <summary>
        /// Resizes the image to fit the size of the window.
        /// </summary>
        /// <param name="a_pGraphics">Graphics device manager used to get the new viewport.</param>
        /// <param name="a_v2PercentAcross">Places the top left corner point of the texture a 
        ///                                 specified percentage of the actual new viewport.</param>
        /// <param name="a_v2DynamicPosition">Allows the resizing to dynamic pass in the new location.</param>
        public void OnResize(GraphicsDeviceManager a_pGraphics, Vector2 a_v2PercentAcross, Vector2 a_v2DynamicPosition)
        {
            if (a_v2DynamicPosition.X > 0)
            {
                m_rScreenPosition.X = (int)a_v2DynamicPosition.X;
            }

            if (a_v2DynamicPosition.Y > 0)
            {
                m_rScreenPosition.Y = (int)a_v2DynamicPosition.Y;
            }

            m_rScreenPosition.Width = (int)(a_pGraphics.GraphicsDevice.Viewport.Width * a_v2PercentAcross.X);
            m_rScreenPosition.Height = (int)(a_pGraphics.GraphicsDevice.Viewport.Height * a_v2PercentAcross.Y);
        }

    }
}
